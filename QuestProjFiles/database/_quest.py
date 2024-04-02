from ._primitive import *
from ._db_config import engine
from ._user import GetUserByToken
from ._block import GetAllTasks


def GetQuestById(quest_id):
    _data = select(engine, "quests", id=quest_id)
    if len(_data) > 0:
        return _data[0]
    return {}


# def GetQuestByInfo(quest_name, short, quest_type, creator_id, start_time, end_time, quest_image):
#     select(engine, "quests", quest_name=quest_name, short=short, quest_type=quest_type,
#            creator_id=creator_id, start_time=start_time, )


def GetAllQuests():
    return select(engine, "quests")


def GetAllCreatedQuests(token):
    user_id = GetUserByToken(token)["id"]
    _data = select(engine, "quests", creator_id=user_id)
    if len(_data) > 0:
        return _data
    return []


def GetAllParticipatedQuests(token):
    user_id = GetUserByToken(token)["id"]
    participations = select(engine, "participation", user_id=user_id)
    if len(participations) > 0:
        quests = []
        for i in participations:
            quests.append(GetQuestById(i["quest_id"]))
        return quests
    return []


def GetQuestParticipants(quest_id):
    participants = select(engine, "participation", quest_id=quest_id)
    if len(participants) > 0:
        users = []
        for participant in participants:
            select(engine, "users", id=participant["user_id"])
        return users
    return []


def GetParticipation(quest_id, user_id):
    _data = select(engine, "participation", quest_id=quest_id, user_id=user_id)
    if len(_data) > 0:
        return _data[0]
    return {}


def GetResults(quest_id):
    return select(engine, "participation", quest_id=quest_id, role_id='0')


def AddQuest(quest_name, short, quest_type, creator_id, start_time, end_time, quest_image):
    columns = ["quest_name", "short", "quest_type", "creator_id", "start_time", "end_time", "quest_image"]
    values = [quest_name, short, quest_type, creator_id, start_time, end_time, quest_image]
    insert(engine, "quests", columns, values)


def ChangeQuestInfo(quest_id, name, change):
    update(engine,
           "quests",
           {name: change},
           {'id': quest_id})


def DeleteQuestById(quest_id):
    delete(engine, 'quests', id=quest_id)
    delete(engine, 'participation', quest_id=quest_id)
    blocks = select(engine, 'blocks', quest_id=quest_id)
    delete(engine, 'blocks', quest_id=quest_id)
    for block in blocks:
        tasks = select(engine, 'tasks', block_id=block["id"])
        for task in tasks:
            delete(engine, "answers", task_id=task['id'])
        delete(engine, 'tasks', block_id=block['id'])


def RemoveUserFromQuest(quest_id, user_id):
    delete(engine, 'participation', user_id=user_id, quest_id=quest_id)
    _blocks = GetAllBlocks(quest_id)
    for _block in _blocks:
        _tasks = GetAllTasks(_block["id"])
        for _task in _tasks:
            delete(engine, "answer", user_id=user_id, task_id=_task["id"])


def CreateBlock(quest_id, block_name, block_num, block_type, min_tasks):
    columns = ["quest_id", "block_name", "block_num", "block_type", "min_tasks"]
    values = [quest_id, block_name, block_num, block_type, min_tasks]
    insert(engine, "blocks", columns, values)


def ChangeBlockInfo(block_id, name, change):
    update(engine, "blocks", {name: change}, {'id': block_id})


def GetBlockByInfo(quest_id, block_name, block_num, block_type):
    _data = select(engine, "blocks",
                   quest_id=quest_id,
                   block_name=block_name,
                   block_num=block_num,
                   block_type=block_type)
    if len(_data) > 0:
        return _data[0]
    return {}


def GetAllBlocks(quest_id):
    return select(engine, "blocks", quest_id=quest_id)


def AddParticipant(quest_id, user_id):
    columns = ["quest_id", "user_id"]
    values = [quest_id, user_id]
    insert(engine, "participation", columns, values)
    _blocks = GetAllBlocks(quest_id)
    for _block in _blocks:
        _tasks = GetAllTasks(_block["id"])
        for _task in _tasks:
            task_columns = ["task_id", "user_id"]
            task_values = [_task['id'], user_id]
            insert(engine, "answers", task_columns, task_values)

# def DuplicateQuest(quest_id):
#
#     _blocks = GetAllBlocks(quest_id)
#     for _block in _blocks:
#
#
# def DuplicateBlock(new_quest_id, block_name, block_num, block_type, min_tasks):
#     CreateBlock(new_quest_id, block_name, block_num, block_type, min_tasks)
