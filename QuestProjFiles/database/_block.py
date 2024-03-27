from ._primitive import *
from ._db_config import engine


def GetAllTasks(block_id):
    return select(engine, "tasks", block_id=block_id)


def CreateTask(_block_id, _task_num, _task_type, _task_time, _description, _max_points, _min_points, _vital):
    columns = ["block_id", "task_num", "task_type", "task_time", "description", "max_points", "min_points", "vital"]
    values = [_block_id, _task_num, _task_type, _task_time, _description, _max_points, _min_points, _vital]
    insert(engine, "tasks", columns, values)


def GetBlockById(block_id):
    return select(engine, "blocks", id=block_id)


def ChangeBlockVits(block_id):
    vitals = GetBlockById(block_id)["vits"]
    update(engine, "blocks", {"vitals": vitals + 1}, {'id': block_id})


def ChangeBlock(block_id, block_name, block_num, block_type, min_tasks):
    update(engine, "blocks", {"block_name": block_name, "block_num": block_num, "block_type": block_type, "min_tasks": min_tasks}, {"id": block_id})


def DeleteBlock(block_id):
    tasks = GetAllTasks(block_id)
    delete(engine, "blocks", id=block_id)
    for task in tasks:
        delete(engine, "blocks", id=task["id"])
