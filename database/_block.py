from ._primitive import *
from ._db_config import engine


def GetAllTasks(id):
    return select(engine, "tasks", block_id=id)

def CreateTask(_block_id, _task_type, _task_time, _description, _max_points, _min_points, _vital):
    columns = ["block_id", "task_type", "task_time", "description", "max_points", "min_points", "vital"]
    values = [_block_id, _task_type, _task_time, _description, _max_points, _min_points, _vital]
    insert(engine, "tasks", columns, values)

def GetBlockById(id):
    return select(engine, "blocks", id=id)

def ChangeBlockVits(id):
    vitals = GetBlockById(id)["vits"]
    update(engine, "blocks", {"vitals": vitals + 1}, {'id': id})

def DeleteBlock(id):
    tasks = GetAllTasks(id)
    delete(engine, "blocks", id=id)
    for task in tasks:
        delete(engine, "blocks", id=task["id"])
