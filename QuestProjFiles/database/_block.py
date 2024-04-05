from ._primitive import *
from ._db_config import engine


def GetAllTasks(block_id):
    _data = select(engine, "tasks", block_id=block_id)
    if len(_data) > 0:
        return _data
    return []


def CreateTask(_block_id, _task_num, _task_type, _task_time, _description, _question,
               _max_points, _min_points, _answer, _vital, _images):
    columns = ["block_id", "task_num", "task_type", "task_time", "description", "question",
               "max_points", "min_points", "answer", "vital", "images"]
    values = [_block_id, _task_num, _task_type, _task_time, _description, _question,
              _max_points, _min_points, _answer, _vital, _images]
    insert(engine, "tasks", columns, values)


def GetTaskByInfo(_block_id, _task_num, _task_type, _task_time, _description, _question,
                  _max_points, _min_points, _answer, _vital):
    return select(engine, 'tasks', block_id=_block_id,
                  task_num=_task_num,
                  task_type=_task_type,
                  task_time=_task_time,
                  description=_description,
                  question=_question,
                  answer=_answer,
                  vital=_vital)


def GetBlockById(block_id):
    _data = select(engine, "blocks", id=block_id)
    if len(_data) > 0:
        return _data[0]
    return {}


def ChangeBlockVits(block_id):
    vitals = GetBlockById(block_id)["vits"]
    update(engine, "blocks", {"vits": vitals + 1}, {'id': block_id})


def ChangeBlock(block_id, block_name, block_num, block_type, min_tasks):
    update(engine, "blocks",
           {"block_name": block_name, "block_num": block_num, "block_type": block_type, "min_tasks": min_tasks},
           {"id": block_id})


def DeleteBlock(block_id):
    tasks = GetAllTasks(block_id)
    delete(engine, "blocks", id=block_id)
    for task in tasks:
        delete(engine, "blocks", id=task["id"])
        delete(engine, "answers", task_id=task['id'])


def DuplicateTask(_new_block_id, _block_id, _task_id, _task_num, _task_type, _task_time,
                  _description, _question, _max_points, _min_points, _answer, _vital):
    # num_tasks = len(GetTaskByInfo(_block_id, _task_num, _task_type, _task_time,
    #                 _description, _question, _max_points, _min_points, _answer, _vital))
    num_tasks = len(GetAllTasks(_new_block_id))
    CreateTask(_new_block_id, num_tasks, _task_type, _task_time, _description, _question,
               _max_points, _min_points, _answer, _vital)
