from flask import json

from .srv import app, session, redirect, request, render_template

from database._tasks import *
from .srv import app


@app.route('/tasks/<int:id>', methods=["GET"])
def task(id):
    try:
        _data = GetTask(id)
        if len(_data) == 0:
            return {"status": "ERR", "message": "There is no such task"}
        return {"status": "OK", "message": json.dumps(_data)}
    except Exception as e:
        return {"status": "ERR", "message": e}


@app.route('/tasks/<int:id>', methods=["PUT"])
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
        return {"status": "ERR", "message": e}


@app.route('/tasks/<int:id>', methods=["DELETE"])
def delete_task(id):
    try:
        if GetTask(id):
            DeleteTask(id)
            return {"status": "OK", "message": "Task successfully deleted"}
        else:
            return {"status": "ERR", "message": "Task doesn't exist"}

    except Exception as e:
        return {"status": "ERR", "message": e}
