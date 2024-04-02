# -*- coding: utf-8 -*-

from flask import json

from .srv import request

from ..database._tasks import *
from ..database import GetBlockById, GetQuestById, TokenExpired, GetUserByToken
from .srv import app


@app.route('/task/<string:task_id>', methods=["POST"])
def task(task_id):
    try:
        _task = GetTask(task_id)
        if len(_task) == 0:
            return {"status": "ERR", "message": "Task doesn't exist"}

        _block = GetBlockById(_task['block_id'])

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
            _ans = GetUserProgress(_user["id"], task_id)
            _task['user_progress'] = _ans

        if _user['id'] == _quest["creator_id"]:
            _task["is_creator"] = True
        else:
            _task["is_creator"] = False

        return json.dumps({"status": "OK", "message": _task}, ensure_ascii=False).encode("utf8")
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/task/<string:task_id>/giveans', methods=["POST"])
def give_answer(task_id):
    try:
        _task = GetTask(task_id)
        if len(_task) == 0:
            return {"status": "ERR", "message": "There is no such task"}

        _block = GetBlockById(_task['block_id'])

        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if len(_user) == 0 or len(_quest) == 0:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _status = _json['status']
        _points = _json["points"]

        AddAnswer(_quest['id'], task_id, _user['id'], _status, _points)

        return {"status": "OK", "message": "Answer added successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/task/<string:task_id>', methods=["PUT"])
def change_task(task_id):
    try:
        _task = GetTask(task_id)

        if len(_task) == 0:
            return {"status": "ERR", "message": "There is no such task"}

        _block = GetBlockById(_task['block_id'])

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
            return {"status": "ERR", "message": "Unauthorized attempt"}

        _task_time = _json["task_time"]
        _description = _json["description"]
        _max = _json["max_points"]
        _min = _json["min_points"]
        _vital = _json["vital"]

        if _task_time:
            ChangeTaskInfo(task_id, "task_time", _task_time)
        if _description:
            ChangeTaskInfo(task_id, "description", _description)
        if _max:
            ChangeTaskInfo(task_id, "max_points", _max)
        if _min:
            ChangeTaskInfo(task_id, "min_points", _min)
        if _vital:
            ChangeTaskInfo(task_id, "vital", _vital)
        return {"status": "OK", "message": "Task successfully changed"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/task/<string:task_id>/delete', methods=["DELETE"])
def delete_task(task_id):
    try:
        _task = GetTask(task_id)

        if len(_task) == 0:
            return {"status": "ERR", "message": "There is no such task"}

        _block = GetBlockById(_task['block_id'])

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
            return {"status": "ERR", "message": "Unauthorized attempt"}

        DeleteTask(task_id)
        return {"status": "OK", "message": "Task successfully deleted"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
