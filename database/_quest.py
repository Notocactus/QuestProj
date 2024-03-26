from ._primitive import *
from ._db_config import engine
from ._user import GetUserByToken


def GetQuestById(quest_id):
    return select(engine, "quests", quest_id=quest_id)


def GetAllQuests():
    return select(engine, "quests")


def GetAllCreatedQuests(token):
    id = GetUserByToken(token)["id"]
    return select(engine, "quests", creator_id=id)


def GetAllParticipatedQuests(token):
    id = GetUserByToken(token)["id"]
    participations = select(engine, "participation", user_id=id)
    quests = []
    for i in participations:
        quests.append(GetQuestById(i["quest_id"]))
    return quests


def GetQuestParticipants(id):
    participants = select(engine, "participation", quest_id=id)
    users = []
    for participant in participants:
        select(engine, "users", id=participant["user_id"])
    return users


def AddQuest(quest_name, short, quest_type, creator_id, start_time, end_time, quest_image):
    columns = ["quest_name", "short", "quest_type", "creator_id", "start_time", "end_time", "quest_image"]
    values = [quest_name, short, quest_type, creator_id, start_time, end_time, quest_image]
    insert(engine, "quests", columns, values)


def ChangeQuestInfo(id, name, change):
    update(engine,
           "quests",
           {name: change},
           {'id': id})

def DeleteQuestById(id):
    delete(engine, 'quests', id=id)
    blocks = select(engine, 'blocks', 'id', quest_id=id)
    delete(engine, 'blocks', quest_id=id)
    for block in blocks:
        delete(engine, 'tasks', block_id=block['id'])


def RemoveUserFromQuest(id, token):
    user = GetUserByToken(token)
    delete(engine, 'participation', user_id=user['id'], quest_id=id)


def CreateBlock(quest_id, block_num, block_type):
    columns = ["quest_id", "block_num", "block_type"]
    values = [quest_id, block_num, block_type]
    insert(engine, "blocks", columns, values)


def Change(id, change):
    update(engine, "blocks", {"block_num": change}, {'id': id})


def GetBlockByInfo(quest_id, block_num, block_type):
    return select(engine, "blocks", quest_id=quest_id, block_num=block_num, block_type=block_type)


def GetAllBlocks(quest_id):
    select(engine, "blocks", quest_id=quest_id)
