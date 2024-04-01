from ._primitive import *
from ._db_config import engine
from time import *


def RegisterUser(last_name, first_name, patronym):
    columns = ['first_name', 'last_name', 'patronym']
    values = [first_name, last_name, patronym]
    insert(engine, "users", columns, values)
    return select(engine, "users", last_name=last_name, first_name=first_name, patronym=patronym)[0]


def RegisterSession(user_id, token, expiry_time, session_hash):
    columns = ['user_id', 'auth_token', 'expiry_time', 'session_hash']
    values = [user_id, token, expiry_time, session_hash]
    insert(engine, "session", columns, values)


def GetAuthToken(session_hash):
    return select(engine, "session", session_hash=session_hash)[0]


def TokenExpired(hauth_token):
    _session = select(engine, "session", auth_token=hauth_token)[0]
    if not _session:
        return True
    if _session["expiry_time"] < str(time()):
        delete(engine, "session", auth_token=hauth_token)
        return True
    else:
        return False


def GetUserByToken(hauth_token):
    _user_id = select(engine, "session", auth_token=hauth_token)[0]["user_id"]
    return select(engine, "users", id=_user_id)[0]


def GetUserByInfo(last_name, first_name, patronym):
    data = select(engine, "users", last_name=last_name, first_name=first_name, patronym=patronym)
    if len(data) > 0:
        return data[0]
    return None


def DeleteUser(user_id):
    delete(engine, 'users', id=user_id)
