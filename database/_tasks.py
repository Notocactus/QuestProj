from ._primitive import *
from ._db_config import engine


def GetTask(id):
    return select(engine, "tasks", id=id)

def ChangeTaskInfo(id, name, change):
    update(engine,
           "tasks",
           {name: change},
           {'id': id})

def DeleteTask(id):
    delete(engine, "tasks", )