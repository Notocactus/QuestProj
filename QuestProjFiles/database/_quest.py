from ._primitive import *
from ._db_config import engine
from ._user import GetUserByToken
from ._block import GetAllTasks, DuplicateTask


def GetQuestById(quest_id):
    _data = select(engine, "quests", id=quest_id)
    if len(_data) > 0:
        return _data[0]
    return {}


def GetUserById(user_id):
    _data = select(engine, "users", id=user_id)
    if len(_data) > 0:
        return _data[0]
    return {}


def GetQuestByInfo(quest_name, short, quest_type, creator_id, start_time, end_time, quest_image):
    _data = select(engine, "quests", quest_name=quest_name, short=short, quest_type=quest_type,
                   creator_id=creator_id, start_time=start_time, end_time=end_time, quest_image=quest_image)
    if len(_data) > 0:
        return _data[0]
    return {}


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
            users.append(GetUserById(participant["user_id"]))
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
    groups = select(engine, "groups", quest_id=quest_id)
    delete(engine, "groups", quest_id=quest_id)
    for group in groups:
        delete(engine, "group_participants", group_id=group["id"])


def RemoveUserFromQuest(quest_id, user_id):
    delete(engine, 'participation', user_id=user_id, quest_id=quest_id)
    _blocks = GetAllBlocks(quest_id)
    for _block in _blocks:
        _tasks = GetAllTasks(_block["id"])
        for _task in _tasks:
            delete(engine, "answers", user_id=user_id, task_id=_task["id"])


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


def AddParticipant(quest_id, user_id, role=0):
    columns = ["quest_id", "user_id", "role_id"]
    values = [quest_id, user_id, role]
    insert(engine, "participation", columns, values)
    _blocks = GetAllBlocks(quest_id)
    for _block in _blocks:
        _tasks = GetAllTasks(_block["id"])
        for _task in _tasks:
            task_columns = ["task_id", "user_id"]
            task_values = [_task['id'], user_id]
            insert(engine, "answers", task_columns, task_values)


def DuplicateQuest(new_quest_id, quest_id):
    _blocks = GetAllBlocks(quest_id)
    for _block in _blocks:
        DuplicateBlock(new_quest_id, quest_id, _block['quest_id'], _block["block_name"], _block["block_num"],
                       _block["block_type"], _block["min_tasks"])


def DuplicateBlock(new_quest_id, quest_id, block_id, block_name, block_num, block_type, min_tasks):
    new_block_num = len(GetAllBlocks(new_quest_id))
    CreateBlock(new_quest_id, block_name, new_block_num, block_type, min_tasks)
    new_block_id = GetBlockByInfo(new_quest_id, block_name, new_block_num, block_type)['id']
    _tasks = GetAllTasks(block_id)
    for _task in _tasks:
        DuplicateTask(new_block_id, _task["block_id"], _task["id"], _task["task_num"], _task["task_type"],
                      _task["task_time"], _task["description"], _task["question"],
                      _task["max_points"], _task["min_points"], _task["answer"], _task["vital"])
    return new_block_id


def GetGroupByInfo(quest_id, group_name):
    _data = select(engine, "groups", quest_id=quest_id, group_name=group_name)
    if len(_data) > 0:
        return _data[0]
    return {}


def GetGroupById(group_id):
    _data = select(engine, "groups", id=group_id)
    if len(_data) > 0:
        return _data[0]
    return {}


def GetAllGroups(quest_id):
    _data = select(engine, "groups", quest_id=quest_id)
    return _data


def GetGroupParticipationByInfo(quest_id, user_id):
    _groups = select(engine, "group_participants", user_id=user_id)
    for _group in _groups:
        curr = GetGroupById(_group['group_id'])
        if curr['quest_id'] == quest_id:
            return curr
    return {}


def MakeGroup(quest_id, user_id, group_name):
    columns = ["quest_id", "group_name", "leader_id"]
    values = [quest_id, group_name, user_id]
    insert(engine, "groups", columns, values)
    _group_id = GetGroupByInfo(quest_id, group_name)['id']
    AddGroupParticipant(_group_id, user_id, 1)


def GetGroupParticipants(group_id):
    _data = select(engine, "group_participants", group_id=group_id)
    users = []
    for _item in _data:
        user = GetUserById(_item["user_id"])
        users.append(user)
    return users


def AddGroupParticipant(group_id, user_id, is_leader=0):
    columns = ["group_id", "user_id", "is_leader"]
    values = [group_id, user_id, is_leader]
    insert(engine, "group_participants", columns, values)


def RemoveGroupParticipant(group_id, user_id):
    delete(engine, "group_participants", group_id=group_id, user_id=user_id)


def RemoveGroup(group_id):
    delete(engine, 'groups', id=group_id)
    delete(engine, 'group_participants', group_id=group_id)


def ChangeGroupName(group_id, new_group_name):
    update(engine, "groups", {'group_name': new_group_name}, {"id": group_id})
