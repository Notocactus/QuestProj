from ._primitive import *
from ._db_config import engine


def GetAllTasks(block_id):
    _data = select(engine, "tasks", block_id=block_id)
    if len(_data) > 0:
        return _data
    return []


def CreateTask(_block_id, _task_num, _task_type, _task_time, _description, _question,
               _max_points, _min_points, _answer, _vital):
    columns = ["block_id", "task_num", "task_type", "task_time", "description", "question",
               "max_points", "min_points", "answer", "vital"]
    values = [_block_id, _task_num, _task_type, _task_time, _description, _question,
              _max_points, _min_points, _answer, _vital]
    insert(engine, "tasks", columns, values)
    return select(engine, 'tasks', block_id=_block_id,
                  task_num=_task_num,
                  task_type=_task_type,
                  description=_description,
                  question=_question,
                  answer=_answer,
                  vital=_vital)[0]


def GetBlockById(block_id):
    _data = select(engine, "blocks", id=block_id)
    if len(_data) > 0:
        return _data[0]
    return {}


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
        delete(engine, "answers", task_id=task['id'])
