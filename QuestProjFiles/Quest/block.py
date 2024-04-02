# -*- coding: utf-8 -*-

from flask import json

from .srv import app, request
from ..database import GetUserProgress, ChangeTaskInfo

from ..database._block import *
from ..database._user import TokenExpired, GetUserByToken
from ..database._quest import GetQuestById
from ..database._tasks import GetTask


@app.route('/block/<string:block_id>', methods={"PUT"})
def change_block(block_id):
    try:
        _block = GetBlockById(block_id)

        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            return {"response": "ERR", "message": "Unauthorized attempt"}

        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _block_name = _json["block_name"]
        _block_num = _json["block_num"]
        _block_type = _json["block_type"]
        _min_tasks = _json["min_tasks"]
        ChangeBlock(block_id, _block_name, _block_num, _block_type, _min_tasks)
        return {"status": "OK", "message": "Block info successfully changed"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>', methods=["POST"])
def block(block_id):
    try:
        _block = GetBlockById(block_id)
        if len(_block) == 0:
            return {"status": "ERR", "message": "Block doesn't exist"}

        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _tasks = GetAllTasks(block_id)
        if len(_tasks) > 0:
            _tasks = sorted(_tasks, key=lambda d: d['task_num'])

        # if not creator
        if _user['id'] != _quest["creator_id"]:
            for _task in _tasks:
                _progress = GetUserProgress(_user["id"], _task["id"])
                _task["user_progress"] = _progress

        _block["tasks_list"] = _tasks

        if _user['id'] == _quest["creator_id"]:
            _block["is_creator"] = True
        else:
            _block["is_creator"] = False
        return json.dumps({"status": "OK", "message": _block}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>/task', methods=["POST"])
def create_task(block_id):
    try:
        _block = GetBlockById(block_id)
        if len(_block) == 0:
            return {"status": "ERR", "message": "Block doesn't exist"}

        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            return {"response": "ERR", "message": "Unauthorized attempt"}

        _task_num = _json["task_num"]
        _task_type = _json["task_type"]
        _task_time = _json["task_time"]
        _description = _json["description"]
        _question = _json["question"]
        _max = _json["max_points"]
        _min = _json["min_points"]
        _answer = _json["answer"]
        _vital = _json["vital"]

        CreateTask(block_id, _task_num, _task_type, _task_time,
                   _description, _question, _max, _min, _answer, _vital)
        _task = GetTaskByInfo(block_id, _task_num, _task_type, _task_time,
                              _description, _question, _max, _min, _answer, _vital)[0]
        _ret = {"task_id": _task["id"]}
        if _vital == "1" or int(_vital) == 1:
            ChangeBlockVits(block_id)

        return json.dumps({"status": "OK", "message": _ret})
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>/tasks', methods=['PUT'])
def tasks(block_id):
    if request.method == "PUT":
        try:
            _block = GetBlockById(block_id)

            if len(_block) == 0:
                return {"status": "ERR", "message": "Block doesn't exist"}

            _json = request.data
            _json = json.loads(_json)

            _hauth_token = _json["auth_token"]
            if TokenExpired(_hauth_token):
                return {"status": "ERR", "message": "Registrate first"}

            _user = GetUserByToken(_hauth_token)
            _quest = GetQuestById(_block["quest_id"])

            if len(_user) == 0 or len(_quest) == 0:
                return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

            if _user['id'] != _quest["creator_id"]:
                return {"status": "ERR", "message": "Unauthorized attempt"}

            _tasks = _json['tasks_list']
            for _task in _tasks:
                ChangeTaskInfo(_task['id'], "task_num", _task['task_num'])
            return {'status': "OK", "message": "Order changed"}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>/delete', methods=["DELETE"])
def delete_block(block_id):
    try:
        _block = GetBlockById(block_id)
        if len(_block) == 0:
            return {"status": "ERR", "message": "Block doesn't exist"}

        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            return {"response": "ERR", "message": "Unauthorized attempt"}

        if len(GetBlockById(block_id)) > 0:
            DeleteBlock(block_id)
            return {"status": "OK", "message": "Block successfully deleted"}
        else:
            return {"status": "ERR", "message": "Block doesn't exist"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


# @app.route('/block/<string:block_id>/duplicate', methods=["POST"])
# def duplicate_task(block_id):
#     try:
#         _block = GetBlockById(block_id)
#         if len(_block) == 0:
#             return {"status": "ERR", "message": "Block doesn't exist"}
#
#         _json = request.data
#         _json = json.loads(_json)
#
#         _hauth_token = _json["auth_token"]
#         if TokenExpired(_hauth_token):
#             return {"status": "ERR", "message": "Registrate first"}
#
#         _user = GetUserByToken(_hauth_token)
#         _quest = GetQuestById(_block["quest_id"])
#
#         if len(_user) == 0 or len(_quest) == 0:
#             return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}
#
#         # if is not creator
#         if _user['id'] != _quest["creator_id"]:
#             return {"status": "ERR", "message": "Unauthorized attempt"}
#
#         _task_id = _json["task_id"]
#         _task = GetTask(_task_id)
#         if len(_task) == 0:
#             return {"status": "ERR", "message": "There is no such task"}
#
#         DuplicateTask(block_id, _task["task_num"], _task["task_type"],
#                       _task["task_time"], _task["description"], _task["question"],
#                       _task["max_points"], _task["min_points"], _task["answer"], _task["vital"])
#         return {'status': 'OK', 'message': 'Task duplicated successfully'}
#     except Exception as e:
#         return {"status": "ERR", "message": f"{e}"}
