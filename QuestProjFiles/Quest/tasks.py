from flask import json

from .srv import request

from ..database._tasks import *
from ..database import GetBlockById, GetQuestById, TokenExpired, GetUserByToken
from .srv import app


@app.route('/tasks/<string:task_id>', methods=["GET"])
def task(task_id):
    try:
        _task = GetTask(task_id)

        if len(_task) == 0:
            return {"status": "ERR", "message": "There is no such task"}

        _block = GetBlockById(_task['block_id'])
        # _header = request.headers
        # _hauth_token = _header["auth_token"]
        _hauth_token = request.json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            _ans = GetUserProgress(_user["id"], task_id)
            _task['user_progress'] = _ans

        return {"status": "OK", "message": json.dumps(_task)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/tasks/<string:task_id>/giveans', methods=["POST"])
def give_answer(task_id):
    try:
        _task = GetTask(task_id)

        if len(_task) == 0:
            return {"status": "ERR", "message": "There is no such task"}

        _block = GetBlockById(_task['block_id'])
        # _header = request.headers
        # _hauth_token = _header["auth_token"]
        _json = request.json
        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _status = _json['status']
        _correct = _json['correct']
        _points = _json["points"]

        AddAnswer(_quest['id'], task_id, _user['id'], _status, _correct, _points)

        return {"status": "OK", "message": json.dumps(_task)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/tasks/<string:task_id>', methods=["PUT"])
def change_task(task_id):
    try:
        _task = GetTask(task_id)

        if len(_task) == 0:
            return {"status": "ERR", "message": "There is no such task"}

        _block = GetBlockById(_task['block_id'])
        _json = request.json
        # _header = request.headers
        # _hauth_token = _header["auth_token"]
        _hauth_token = request.json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            return {"status": "ERR", "message": "Unauthorized attempt"}
        _id = _json["id"]
        _task_time = _json["task_time"]
        _description = _json["description"]
        _max = _json["max_points"]
        _min = _json["min_points"]
        _vital = _json["vital"]

        if _task_time:
            ChangeTaskInfo(_id, "task_time", _task_time)
        if _description:
            ChangeTaskInfo(_id, "description", _description)
        if _max:
            ChangeTaskInfo(_id, "max_points", _max)
        if _min:
            ChangeTaskInfo(_id, "min_points", _min)
        if _vital:
            ChangeTaskInfo(_id, "vital", _vital)
        return {"status": "OK", "message": "Task successfully changed"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/tasks/<string:task_id>', methods=["DELETE"])
def delete_task(task_id):
    try:
        if GetTask(task_id):
            DeleteTask(task_id)
            return {"status": "OK", "message": "Task successfully deleted"}
        else:
            return {"status": "ERR", "message": "Task doesn't exist"}

    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
