from ._primitive import *
from ._db_config import engine
from time import *


def RegisterUser(last_name, first_name, patronym):
    columns = ['first_name', 'last_name', 'patronym']
    values = [first_name, last_name, patronym]
    insert(engine, "users", columns, values)
    return select(engine, "users", last_name=last_name, first_name=first_name, patronym=patronym)['id']


def RegisterSession(user_id, token, expiry_time, session_hash):
    columns = ['user_id', 'token', 'expiry_time', 'session_hash']
    values = [user_id, token, expiry_time, session_hash]
    insert(engine, "session", columns, values)


def GetAuthToken(session_hash):
    return select(engine, "session", session_hash=session_hash)


def TokenExpired(hauth_token):
    _session = select(engine, "session", auth_token=hauth_token)
    if not _session:
        return True
    if _session["expiry_time"] < str(time()):
        delete(engine, "session", auth_token=hauth_token)
        return True
    else:
        return False


def GetUserByToken(hauth_token):
    _user_id = select(engine, "session", auth_token=hauth_token)["user_id"]
    return select(engine, "users", id=_user_id)


def GetUserByInfo(last_name, first_name, patronym):
    return select(engine, "users", last_name=last_name, first_name=first_name, patronym=patronym)


def DeleteUser(user_id):
    delete(engine, 'users', id=user_id)
