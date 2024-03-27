from flask import json

from ..database import TokenExpired, ChangeBlockInfo
from .srv import app, session, redirect, request, render_template

from ..database._block import *


@app.route('/block/<int:block_id>', methods={"PUT"})
def change_block(block_id):
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _json = request.json()
        _block_name = _json["block_name"]
        _block_num = _json["block_num"]
        _block_type = _json["block_type"]
        _min_tasks = _json["min_tasks"]
        ChangeBlock(block_id, _block_name, _block_num, _block_type, _min_tasks)
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<int:block_id>/tasks', methods=["GET"])
def block(block_id):
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _data = GetAllTasks(block_id)
        if len(_data) == 0:
            return {"status": "ERR", "message": "There are no tasks yet"}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<int:id>', methods=["POST"])
def create_task():
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        # _user = GetUserByToken(_hauth_token)
        # _quest = GetQuestById(quest_id)
        #
        # if not _user or not _quest:
        #     return {"status": "ERR", "message": "User doesn't exist or quest doesn't exist"}

        _json = request.json
        _block_id = _json["block_id"]
        _task_num = _json["task_num"]
        _task_type = _json["task_type"]
        _task_time = _json["task_time"]
        _description = _json["description"]
        _max = _json["max_points"]
        _min = _json["min_points"]
        _vital = _json["vital"]

        CreateTask(_block_id, _task_num, _task_type, _task_time, _description, _max, _min, _vital)

        if _vital == "true" or _vital is True:
            ChangeBlockVits(_block_id)

        return {"status": "OK", "message": "Task successfully created"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/block/<int:block_id>', methods=["DELETE"])
def delete_block(block_id):
    try:
        if GetBlockById(block_id):
            DeleteBlock(block_id)
            return {"status": "OK", "message": "Block successfully deleted"}
        else:
            return {"status": "ERR", "message": "Block doesn't exist"}

    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
