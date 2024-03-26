from ._primitive import *
from ._db_config import engine


def GetTask(task_id):
    return select(engine, "tasks", id=task_id)


def GetUserProgress(user_id, task_id):
    return select(engine, "answers", user_id=user_id, task_id=task_id)


def ChangeTaskInfo(id, name, change):
    update(engine,
           "tasks",
           {name: change},
           {'id': id})


def DeleteTask(id):
    delete(engine, "tasks", )