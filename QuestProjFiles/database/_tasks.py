from ._primitive import *
from ._db_config import engine


def GetTask(task_id):
    return select(engine, "tasks", id=task_id)


def GetUserProgress(user_id, task_id):
    return select(engine, "answers", user_id=user_id, task_id=task_id)


def ChangeTaskInfo(task_id, name, change):
    update(engine,
           "tasks",
           {name: change},
           {'id': task_id})


def AddAnswer(quest_id, task_id, user_id, status, correct, points):
    update(engine, "answers", {'status': status, "correct": correct, "points": points}, {"task_id": task_id, "user_id": user_id})
    _participation = select(engine, "participation", quest_id=quest_id, user_id=user_id)
    _user_score = _participation["user_score"]
    _user_score += points
    update(engine, "participation", {"user_score": _user_score}, {"id":_participation["id"]})


def DeleteTask(task_id):
    delete(engine, "tasks", id=task_id)