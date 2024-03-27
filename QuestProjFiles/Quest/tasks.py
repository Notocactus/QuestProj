from flask import json

from .srv import request

from QuestProjFiles.database._tasks import *
from .srv import app


@app.route('/tasks/<int:task_id>', methods=["GET"])
def task(task_id):
    try:
        _data = GetTask(task_id)
        if len(_data) == 0:
            return {"status": "ERR", "message": "There is no such task"}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/tasks/<int:task_id>', methods=["PUT"])
def change_task():
    try:
        _json = request.json
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


@app.route('/tasks/<int:task_id>', methods=["DELETE"])
def delete_task(task_id):
    try:
        if GetTask(task_id):
            DeleteTask(task_id)
            return {"status": "OK", "message": "Task successfully deleted"}
        else:
            return {"status": "ERR", "message": "Task doesn't exist"}

    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}
