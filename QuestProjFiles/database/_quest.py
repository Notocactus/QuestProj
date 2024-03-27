from ._primitive import *
from ._db_config import engine
from ._user import GetUserByToken


def GetQuestById(quest_id):
    return select(engine, "quests", quest_id=quest_id)


def GetAllQuests():
    return select(engine, "quests")


def GetAllCreatedQuests(token):
    user_id = GetUserByToken(token)["id"]
    return select(engine, "quests", creator_id=user_id)


def GetAllParticipatedQuests(token):
    user_id = GetUserByToken(token)["id"]
    participations = select(engine, "participation", user_id=user_id)
    quests = []
    for i in participations:
        quests.append(GetQuestById(i["quest_id"]))
    return quests


def GetQuestParticipants(quest_id):
    participants = select(engine, "participation", quest_id=quest_id)
    users = []
    for participant in participants:
        select(engine, "users", id=participant["user_id"])
    return users


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
    blocks = select(engine, 'blocks', 'id', quest_id=quest_id)
    delete(engine, 'blocks', quest_id=quest_id)
    for block in blocks:
        delete(engine, 'tasks', block_id=block['id'])


def RemoveUserFromQuest(quest_id, user_id):
    delete(engine, 'participation', user_id=user_id, quest_id=quest_id)


def CreateBlock(quest_id, block_num, block_type, min_tasks):
    columns = ["quest_id", "block_num", "block_type", "min_tasks"]
    values = [quest_id, block_num, block_type, min_tasks]
    insert(engine, "blocks", columns, values)


def ChangeBlockInfo(block_id, name, change):
    update(engine, "blocks", {name: change}, {'id': block_id})


def GetBlockByInfo(quest_id, block_num, block_type):
    return select(engine, "blocks", quest_id=quest_id, block_num=block_num, block_type=block_type)


def GetAllBlocks(quest_id):
    select(engine, "blocks", quest_id=quest_id)
