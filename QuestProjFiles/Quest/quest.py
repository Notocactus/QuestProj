# -*- coding: utf-8 -*-

import json
from ..database import TokenExpired
from .srv import request

from ..database._quest import *
from ..database._block import GetAllTasks
from ..database._tasks import GetUserProgress
from .srv import app


@app.route('/quests', methods=['POST'])
def get_quests():
    try:
        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)

        if len(_user) == 0:
            return {"status": "ERR", "message": "User doesn't exist"}

        _created_quests = GetAllCreatedQuests(_hauth_token)
        _participated_quests = GetAllParticipatedQuests(_hauth_token)

        _data = {"created_quests": _created_quests, "participated_quests": _participated_quests}

        if len(_created_quests) == 0 and len(_participated_quests) == 0:
            return {"status": "ERR", "message": "There are no quests yet"}
        return json.dumps({"status": "OK", "message": _data}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/participants', methods=["POST"])
def get_quest_participants(quest_id):
    try:
        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        if quest_id:
            _data = {"participants": GetQuestParticipants(quest_id)}
            if len(_data) == 0:
                return {"status": "ERR", "message": "There are no participants yet"}
            if _user['id'] == _quest["creator_id"]:
                _data["is_creator"] = True
            else:
                _data["is_creator"] = False
            return json.dumps({"status": "OK", "message": _data}, ensure_ascii=False).encode("utf8")
        else:
            return {"status": "ERR", "message": "Something went terribly wrong"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/create', methods=["POST"])
def create_quest():
    try:
        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        # How to save files?
        # _quest_image = request.files["quest_image"]
        _quest_image_url = ""
        _quest_name = _json['quest_name']
        _short = _json['short']
        _quest_type = _json['quest_type']
        _creator_id = GetUserByToken(_hauth_token)['id']
        _start_time = _json['start_time']
        _end_time = _json['end_time']
        AddQuest(_quest_name, _short, _quest_type, _creator_id, _start_time, _end_time, _quest_image_url)
        return {"status": "OK", "message": "Quest created successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>', methods=["POST", "PUT"])
def quest(quest_id):
    if request.method == "POST":
        try:
            _json = request.data
            _json = json.loads(_json)

            _hauth_token = _json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if len(_user) == 0 or len(_quest) == 0:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            # if not creator
            if _user["id"] != _quest["creator_id"]:
                _blocks = GetAllBlocks(quest_id)
                for _block in _blocks:
                    _tasks = GetAllTasks(_block["id"])
                    for _task in _tasks:
                        _progress = GetUserProgress(_user["id"], _task["id"])
                        _task["user_progress"] = _progress
                    _tasks = sorted(_tasks, key=lambda d: d["task_num"])
                    _block["tasks_list"] = _tasks
                _blocks = sorted(_blocks, key=lambda d: d["block_num"])
                _quest["blocks_list"] = _blocks

            # if is creator
            else:
                _blocks = GetAllBlocks(quest_id)
                for _block in _blocks:
                    _tasks = GetAllTasks(_block["id"])
                    _tasks = sorted(_tasks, key=lambda d: d["task_num"])
                    _block["tasks_list"] = _tasks
                _blocks = sorted(_blocks, key=lambda d: d["block_num"])
                _quest["blocks_list"] = _blocks

            if _user['id'] == _quest["creator_id"]:
                _quest["is_creator"] = True
            else:
                _quest["is_creator"] = False
            _participation = GetParticipation(quest_id, _user["id"])
            if len(_participation) > 0:
                _quest['role'] = _participation['role_id']
            else:
                _quest['role'] = -1

            return json.dumps({"status": "OK", "message": _quest}, ensure_ascii=False).encode("utf8")
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}
    elif request.method == "PUT":
        try:
            _json = request.data
            _json = json.loads(_json)

            _hauth_token = _json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if len(_user) == 0 or len(_quest) == 0:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            if _user["id"] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}

            _new_name = _json["quest_name"]
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


@app.route('/quests/<string:quest_id>/removeparticipant/<string:user_id>', methods=["DELETE"])
def remove_participant(quest_id, user_id):
    try:
        # _header = request.headers
        # _hauth_token = _header["auth_token"]
        _hauth_token = request.json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        if _user['id'] != _quest["creator_id"]:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        RemoveUserFromQuest(quest_id, user_id)
        return {"status": "OK", "message": "Participant removed successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/block', methods=['POST'])
def create_block(quest_id):
    if request.method == 'POST':
        try:
            # _header = request.headers
            # _hauth_token = _header["auth_token"]
            _json = request.json
            _hauth_token = _json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if not _user or not _quest:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            if _user['id'] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}

            _block_name = _json["block_name"]
            _block_type = _json["block_type"]
            _block_num = _json["block_num"]
            _min_tasks = _json["min_tasks"]
            CreateBlock(quest_id, _block_num, _block_type, _min_tasks)
            _data = GetBlockByInfo(quest_id, _block_num, _block_type)
            _ret = {"block_id": _data['id']}
            return {"status": "OK", "message": _ret}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/blocks', methods=['POST', "PUT"])
def get_blocks(quest_id):
    if request.method == "POST":
        try:
            # _header = request.headers
            # _hauth_token = _header["auth_token"]
            _hauth_token = request.json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if not _user or not _quest:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            _data = {"blocks_list": GetAllBlocks(quest_id)}
            if len(_data) == 0:
                return {"status": "ERR", "message": "There are no blocks yet"}
            if _user['id'] == _quest["creator_id"]:
                _data["is_creator"] = True
            else:
                _data["is_creator"] = False
            return {"status": "OK", "message": json.dumps(_data)}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}
    else:
        try:
            # _header = request.headers
            # _hauth_token = _header["auth_token"]
            _json = request.json
            _hauth_token = _json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if not _user or not _quest:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            if _user['id'] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}

            _blocks = _json['blocks_list']
            for _block in _blocks:
                ChangeBlockInfo(_block['id'], "block_num", _block['block_num'])
            return {'status': "OK", "message": "Order changed"}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/joinquest', methods=["POST"])
def participate(quest_id):
    try:
        # _header = request.headers
        # _hauth_token = _header["auth_token"]
        _hauth_token = request.json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        AddParticipant(_quest["id"], _user["id"])
        return {"status": "OK", "message": "User joined quest successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/quitquest', methods=["DELETE"])
def quit(quest_id):
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        RemoveUserFromQuest(_quest["id"], _user["id"])
        return {"status": "ERR", "message": "User quit quest successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/delete", methods=["DELETE"])
def delete_quest(quest_id):
    try:
        _json = request.json
        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        if _user['id'] != _quest["creator_id"]:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        DeleteQuestById(quest_id)
        return {"status": "OK", "message": "Quest deleted successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/results", methods=["POST"])
def results(quest_id):
    try:
        _json = request.json
        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _data = {"results": GetResults(quest_id)}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quest/<string:quest_id>/points", methods=["POST"])
def points(quest_id):
    try:
        _json = request.json
        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _data = {"points": GetParticipation(quest_id, _user["id"])["user_score"]}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
