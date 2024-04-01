# -*- coding: utf-8 -*-

from flask import json

from .srv import app, request
from ..database import GetUserProgress

from ..database._block import *
from ..database._user import *
from ..database._quest import *


@app.route('/block/<string:block_id>', methods={"PUT"})
def change_block(block_id):
    try:
        _block = GetBlockById(block_id)
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

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            return {"response": "ERR", "message": "Unauthorized attempt"}

        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _block_name = _json["block_name"]
        _block_num = _json["block_num"]
        _block_type = _json["block_type"]
        _min_tasks = _json["min_tasks"]
        ChangeBlock(block_id, _block_name, _block_num, _block_type, _min_tasks)
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>', methods=["GET"])
def block(block_id):
    try:
        _block = GetBlockById(block_id)
        # _header = request.headers
        # _hauth_token = _header["auth_token"]
        _hauth_token = request.json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _user = GetUserByToken(_hauth_token)
        _quest = GetQuestById(_block["quest_id"])

        if not _user or not _quest:
            return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _tasks = GetAllTasks(block_id)
        _tasks = sorted(_tasks, key=lambda d: d['task_num'])

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            for _task in _tasks:
                _progress = GetUserProgress(_user["id"], _task["id"])
                _task["user_progress"] = _progress

        _data = GetBlockById(block_id)
        _data["tasks_list"] = _tasks

        if len(_data) == 0:
            if _user['id'] == _quest["creator_id"]:
                _data["is_creator"] = True
            else:
                _data["is_creator"] = False
            return {"status": "ERR", "message": "There are no tasks yet"}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>/tasks', methods=["POST"])
def create_task(block_id):
    try:
        _block = GetBlockById(block_id)
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

        # if is not creator
        if _user['id'] != _quest["creator_id"]:
            return {"response": "ERR", "message": "Unauthorized attempt"}

        _block_id = _json["block_id"]
        _task_num = _json["task_num"]
        _task_type = _json["task_type"]
        _task_time = _json["task_time"]
        _description = _json["description"]
        _max = _json["max_points"]
        _min = _json["min_points"]
        _vital = _json["vital"]

        _task = CreateTask(_block_id, _task_num, _task_type, _task_time, _description, _max, _min, _vital)
        _ret = {"task_id": _task["id"]}
        if _vital == "true" or _vital is True:
            ChangeBlockVits(_block_id)

        return {"status": "OK", "message": _ret}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<string:block_id>', methods=["DELETE"])
def delete_block(block_id):
    try:
        _block = GetBlockById(block_id)
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
            return {"response": "ERR", "message": "Unauthorized attempt"}

        if GetBlockById(block_id):
            DeleteBlock(block_id)
            return {"status": "OK", "message": "Block successfully deleted"}
        else:
            return {"status": "ERR", "message": "Block doesn't exist"}

    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
