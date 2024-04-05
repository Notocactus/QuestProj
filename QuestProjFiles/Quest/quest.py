# -*- coding: utf-8 -*-

import os
import json
from time import time
import  werkzeug  # import secure_filename
from ..database import TokenExpired
from .srv import request
from .constants import FILE_DIR
from ..database._quest import *
from ..database._block import GetAllTasks, GetBlockById
from ..database._tasks import GetUserProgress, ChangeTaskInfo
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

        # if len(_created_quests) == 0 and len(_participated_quests) == 0:
        #     return {"status": "ERR", "message": "There are no quests yet"}
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

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _participants = GetQuestParticipants(quest_id)

        _data = {"participants": _participants}
        # if len(_participants) == 0:
        #     return {"status": "ERR", "message": "There are no participants yet"}
        if _user['id'] == _quest["creator_id"]:
            _data["role"] = -1
        else:
            _data["role"] = GetParticipation(quest_id, _user["id"])["role_id"]
        return json.dumps({"status": "OK", "message": _data}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/create', methods=["POST"])
def create_quest():
    try:
        _json = request.form
        # _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _quest_image = request.files["image"]
        if _quest_image.filename != "defaultImage.png":
            ext = _quest_image.filename.split(".")[-1]
            img_name = f"{time()}.{ext}"
            img_save_path = os.path.join(FILE_DIR, img_name)
            _quest_image.save(img_save_path)
        else:
            img_name = _quest_image.filename
        _quest_name = _json['quest_name']
        _short = _json['short']
        _quest_type = _json['quest_type']
        _creator_id = GetUserByToken(_hauth_token)['id']
        _start_time = _json['start_time']
        _end_time = _json['end_time']
        AddQuest(_quest_name, _short, _quest_type, _creator_id, _start_time, _end_time, img_name)
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

            if _user['id'] == _quest["creator_id"]:
                _quest["role"] = -1
            else:
                _quest["role"] = GetParticipation(quest_id, _user["id"])["role_id"]
                if _quest["role"] == 1:
                    _blocks = GetAllBlocks(quest_id)
                    for _block in _blocks:
                        _tasks = GetAllTasks(_block["id"])
                        for _task in _tasks:
                            if _task["user_id"] == _user["id"]:
                                _quest["npc_task"] = _task
                                return json.dumps({"status": "OK", "message": _quest},
                                                  ensure_ascii=False).encode("utf8")

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
                    for _task in _tasks:
                        _progress = {'id': "0", "task_id": _task["id"],
                                     "user_id": _user["id"], "status": 0, "points": 0}
                        _task["user_progress"] = _progress
                    _tasks = sorted(_tasks, key=lambda d: d["task_num"])
                    _block["tasks_list"] = _tasks
                _blocks = sorted(_blocks, key=lambda d: d["block_num"])
                _quest["blocks_list"] = _blocks

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
                ChangeQuestInfo(quest_id, "quest_name", _new_name)
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
        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if len(_user) == 0 or len(_quest) == 0:
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
            _json = request.data
            _json = json.loads(_json)

            _hauth_token = _json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(quest_id)

            if len(_user) == 0 or len(_quest) == 0:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            if _user['id'] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}

            _block_name = _json["block_name"]
            _block_type = _json["block_type"]
            _block_num = _json["block_num"]
            _min_tasks = _json["min_tasks"]
            CreateBlock(quest_id, _block_name, _block_num, _block_type, _min_tasks)
            _data = GetBlockByInfo(quest_id, _block_name, _block_num, _block_type)
            _ret = {"block_id": _data['id']}
            return json.dumps({"status": "OK", "message": _ret}, ensure_ascii=False).encode("utf8")
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/blocks', methods=['POST', "PUT"])
def get_blocks(quest_id):
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

            _blocks = GetAllBlocks(quest_id)
            if len(_blocks) == 0:
                return {"status": "ERR", "message": "There are no blocks yet"}

            _data = {"blocks_list": _blocks}
            if _user['id'] == _quest["creator_id"]:
                _data["role"] = -1
            else:
                _data["role"] = GetParticipation(quest_id, _user["id"])["role_id"]
            return json.dumps({"status": "OK", "message": _data}, ensure_ascii=False).encode("utf8")
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}
    else:
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

            if _user['id'] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}

            _blocks = _json['blocks_list']
            for _block in _blocks:
                ChangeBlockInfo(_block['id'], "block_num", _block['block_num'])
            return {'status': "OK", "message": "Order changed"}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/joinquest', methods=["POST"])
def join_quest(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _participation = GetParticipation(quest_id, _user["id"])
        if len(_participation) > 0:
            return {"status": "OK", "message": "Already participating"}

        AddParticipant(_quest["id"], _user["id"])
        return {"status": "OK", "message": "User joined quest successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/npcjoinquest', methods=["POST"])
def npc_join(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _participation = GetParticipation(quest_id, _user["id"])
        if len(_participation) > 0:
            return {"status": "OK", "message": "Already participating"}

        _task_id = _json["task_id"]
        ChangeTaskInfo(_task_id, 'user_id', _user["id"])
        AddParticipant(_quest["id"], _user["id"], 1)

        return {"status": "OK", "message": "User joined quest successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/quests/<string:quest_id>/quitquest', methods=["DELETE"])
def quit_quest(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        RemoveUserFromQuest(_quest["id"], _user["id"])
        return {"status": "ERR", "message": "User quit quest successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/delete", methods=["DELETE"])
def delete_quest(quest_id):
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

        if _user['id'] != _quest["creator_id"]:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        DeleteQuestById(quest_id)
        return {"status": "OK", "message": "Quest deleted successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/results", methods=["POST"])
def results(quest_id):
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

        if _quest["quest_type"] == 1:
            _groups = GetAllGroups(quest_id)
            for _group in _groups:
                _group['points'] = GetParticipation(quest_id, _group["leader_id"])["user_score"]
            _quest["results"] = _groups
            return json.dumps({"status": "OK", "message": _quest}, ensure_ascii=False).encode("utf8")

        _results = GetResults(quest_id)
        for i in range(len(_results)):
            _participant = GetUserById(_results[i]['user_id'])
            _participant["points"] = _results[i]["user_score"]
            _results[i] = _participant

        _quest["results"] = _results
        return json.dumps({"status": "OK", "message": _quest}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/points", methods=["POST"])
def points(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _data = {"points": GetParticipation(quest_id, _user["id"])["user_score"]}
        return json.dumps({"status": "OK", "message": _data}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/duplicate", methods=["POST"])
def duplicate_quest(quest_id):
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

        if _user['id'] != _quest["creator_id"]:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        AddQuest(_quest["quest_name"] + "(copy)", _quest["short"], _quest["quest_type"],
                 _quest["creator_id"], _quest["start_time"], _quest["end_time"], _quest["quest_image"])
        _new_quest_id = GetQuestByInfo(_quest["quest_name"] + "(copy)", _quest["short"], _quest["quest_type"],
                                       _quest["creator_id"], _quest["start_time"], _quest["end_time"],
                                       _quest["quest_image"])['id']
        DuplicateQuest(_new_quest_id, quest_id)
        return {"status": "OK", "message": "Quest duplicated successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/duplicateblock", methods=["POST"])
def duplicate_block(quest_id):
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

        if _user['id'] != _quest["creator_id"]:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        _block_id = _json["block_id"]
        _block = GetBlockById(_block_id)
        if len(_block) == 0:
            return {"status": "ERR", "message": "Block doesn't exist"}

        _new_block_id = DuplicateBlock(quest_id, _block['quest_id'], _block["id"], _block["block_name"], _block["block_num"],
                       _block["block_type"], _block["min_tasks"])
        return {"status": "OK", "message": _new_block_id}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/group", methods=["POST"])
def make_group(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group_name = _json["group_name"]
        _group = GetGroupByInfo(quest_id, _group_name)
        if len(_group) > 0:
            return {'status': 'ERR', 'message': 'Group already exists'}

        MakeGroup(quest_id, _user["id"], _group_name)
        return {'status': "OK", "message": "Group added successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/joingroup", methods=["POST"])
def join_group(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group_name = _json["group_name"]
        _group = GetGroupByInfo(quest_id, _group_name)
        if len(_group) == 0:
            return {'status': 'ERR', 'message': "Group doesn't exists"}

        AddGroupParticipant(_group["id"], _user['id'])
        return {'status': "OK", "message": "Joined successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/quitgroup", methods=["DELETE"])
def quit_group(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group = GetGroupParticipationByInfo(quest_id, _user["id"])
        if len(_group) == 0:
            return {"status": "ERR", "message": "User not in group"}

        RemoveGroupParticipant(_group["id"], _user['id'])
        return {'status': "OK", "message": "Quit group successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/removefromgroup", methods=["DELETE"])
def remove_from_group(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _user_id = _json["user_id"]

        _group = GetGroupParticipationByInfo(quest_id, _user['id'])
        if _group["leader_id"] != _user['id']:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        RemoveGroupParticipant(_group["id"], _user_id)
        return {'status': "OK", "message": "Group participant removed successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/removegroup", methods=["DELETE"])
def remove_group(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group = GetGroupParticipationByInfo(quest_id, _user['id'])
        if _group["leader_id"] != _user['id']:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        RemoveGroup(_group["id"])
        return {'status': "OK", "message": "Group removed successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/groupparticipants", methods=["POST"])
def get_group_participants(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group = GetGroupParticipationByInfo(quest_id, _user['id'])
        if len(_group) == 0:
            return {"status": "ERR", "message": "User not in group"}

        _participants = {"participants": GetGroupParticipants(_group["id"]), "user": _user}

        return json.dumps({'status': "OK", "message": _participants}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/checkgroup", methods=["POST"])
def check_group(quest_id):
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

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group = GetGroupParticipationByInfo(quest_id, _user["id"])
        if len(_group) == 0:
            return {"status": "ERR", "message": "User not in group"}
        _data = {"group": _group, "user_id": _user["id"]}
        return json.dumps({'status': "OK", "message": _data}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/checkfinish", methods=["GET"])
def check_finish(quest_id):
    try:
        _quest = GetQuestById(quest_id)
        if len(_quest) == 0:
            return {"status": "ERR", "message": "Quest doesn't exist"}

        _participants = GetQuestParticipants(quest_id)
        _blocks = GetAllBlocks(quest_id)
        for _participant in _participants:
            for _block in _blocks:
                _tasks = GetAllTasks(_block["id"])
                _min_tasks = _block['min_tasks']
                _count = 0
                for _task in _tasks:
                    _status = GetUserProgress(_participant["id"], _task["id"])["status"]
                    if _status == 2:
                        _count += 1
                if _block['block_type'] == 1:
                    if _count < _min_tasks:
                        return json.dumps({"status": "OK", "message": False})
                else:
                    if _count < len(_tasks):
                        return json.dumps({"status": "OK", "message": False})
        return json.dumps({"status": "OK", "message": True})

    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/quests/<string:quest_id>/changegroupname", methods=["PUT"])
def change_group(quest_id):
    try:
        _json = request.data
        _json = json.loads(_json)

        _new_name = _json["group_name"]
        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(quest_id)

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        if _user['id'] == _quest["creator_id"]:
            return {"status": "ERR", "message": "Creator can't participate"}

        _group = GetGroupParticipationByInfo(quest_id, _user['id'])
        if _group["leader_id"] != _user['id']:
            return {"status": "ERR", "message": "Unauthorized attempt"}

        ChangeGroupName(_group["id"], _new_name)
        return {'status': "OK", "message": "Group name changed successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
