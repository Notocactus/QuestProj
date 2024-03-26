from flask import json

from database import TokenExpired
from .srv import app, session, redirect, request, render_template

from ..database._quest import *
from ..database._block import GetAllTasks
from ..database._tasks import GetUserProgress
from .srv import app


def get_created_quests(token):
    return {GetAllCreatedQuests(token)}


def get_participated_quests(token):
    return {GetAllParticipatedQuests(token)}


@app.route('/quests', methods=['GET'])
def get_quests():
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _data = [get_created_quests(_hauth_token), get_participated_quests(_hauth_token)]

        if len(_data) == 0:
            return {"status": "ERR", "message": "There are no quests yet"}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<int:quest_id>/participants', methods=["GET"])
def get_quest_participants(quest_id):
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        if quest_id:
            _data = GetQuestParticipants(quest_id)
            if len(_data) == 0:
                return {"status": "ERR", "message": "There are no participants yet"}
            return {"status": "OK", "message": json.dumps(_data)}
        else:
            return {"status": "ERR", "message": "Something went terribly wrong"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/create', methods=["POST"])
def create_quest():
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        # How to save files
        _quest_image = request.files["quest_image"]
        _quest_image_url = ""
        _json = request.json
        _quest_name = _json['quest_name']
        _short = _json['short']
        _quest_type = _json['full']
        _creator_id = GetUserByToken(_hauth_token)
        _start_time = _json['start_time']
        _end_time = _json['end_time']
        AddQuest(_quest_name, _short, _quest_type, _creator_id, _start_time, _end_time, _quest_image_url)
        return {"status": "OK", "message": "Quest created successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<int:quest_id>', methods=["GET", "PUT"])
def quest(quest_id):
    if request.method == "GET":
        try:
            _header = request.headers
            _hauth_token = _header["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if not _user or not _quest:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}
            # if not creator
            if _user["id"] != _quest["creator_id"]:
                _data = GetQuestById(quest_id)
                _blocks = GetAllBlocks(quest_id)
                for _block in _blocks:
                    _tasks = GetAllTasks(_block["id"])
                    for _task in _tasks:
                        _progress = GetUserProgress(_user["id"], _task["id"])
                        _task["user_progress"] = _progress
                    _block["tasks_list"] = _tasks
                _data["blocks_list"] = _blocks

            # if is creator
            else:
                _data = GetQuestById(quest_id)
                _blocks = GetAllBlocks(quest_id)
                for _block in _blocks:
                    _tasks = GetAllTasks(_block["id"])
                    _block["tasks_list"] = _tasks
                _data["blocks_list"] = _blocks
                if len(_data) == 0:
                    return {"status": "ERR", "message": "There is no such Quest"}
                else:
                    return {"status": "OK", "message": json.dumps(_data)}

        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}
    elif request.method == "PUT":
        try:
            _header = request.headers
            _hauth_token = _header["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if not _user or not _quest:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            if _user["id"] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}
            _json = request.json
            _new_name = _json["name"]
            _new_short = _json["short"]
            _new_start = _json["start_time"]
            _new_end = _json["end_time"]
            if _new_name:
                ChangeQuestInfo(quest_id, "name", _new_name)
            if _new_short:
                ChangeQuestInfo(quest_id, "short", _new_short)
            if _new_start:
                ChangeQuestInfo(quest_id, "start_time", _new_start)
            if _new_end:
                ChangeQuestInfo(quest_id, "end_time", _new_end)
            return {"status": "OK", "message": "Quest changed successfully"}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<int:quest_id>', methods=["DELETE"])
def delete_quest(quest_id):
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        if GetQuestById(quest_id):
            DeleteQuestById(quest_id)
            return {"status": "OK", "message": "Quest successfully deleted"}
        else:
            return {"status": "ERR", "message": "Quest doesn't exist"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<int:quest_id>/removeparticipant/<int:user_id>', methods=["DELETE"])
def remove_participant(quest_id, user_id):
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        RemoveUserFromQuest(quest_id, user_id)
        return {"status": "OK", "message": "Participant removed successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<int:id>/block', methods=['POST'])
def create_block():
    if request.method == 'POST':
        try:
            _json = request.json
            _quest_id = _json["quest_id"]
            _block_type = _json["block_type"]
            _block_num = _json["block_num"]
            CreateBlock(_quest_id, _block_num, _block_type)
            _data = GetBlockByInfo(_quest_id, _block_num, _block_type)
            return {"status": "OK", "message": _data['id']}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<int:id>/blocks', methods=['GET', "PUT"])
def get_blocks(id):
    if request.method == "GET":
        try:
            _data = GetAllBlocks(id)
            if len(_data) == 0:
                return {"status": "ERR", "message": "There are no blocks yet"}
            return {"status": "OK", "message": json.dumps(_data)}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}
    else:
        try:
            _json = request.json
            _blocks = _json['array_of_blocks']
            for block in _blocks:
                Change(block['id'], block['block_num'])
            return {'status': "OK", "message": "Order changed"}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


