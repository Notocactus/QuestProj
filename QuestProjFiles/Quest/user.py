# -*- coding: utf-8 -*-

from flask import json
from .srv import app, request
from ..database import *
from time import time
from hashlib import md5


@app.route("/user/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        try:
            _time = str(time())
            _json = request.form

            _timestamp = _json["timestamp"]
            _hash = _json["hash"]
            _user = _json["user"].split()
            _role = _json["role"]
            _token = _json["token"]
            _nonce = _json["nonce"]

            # # validate the received values
            # if _hauth_token != _token:
            #     return {"status": "ERR", "message": "Unauthorized request"}

            _auth_token = md5((_token + _hash + _time).encode()).hexdigest()

            _user_obj = GetUserByInfo(_user[0], _user[1], _user[2])
            if len(_user_obj) == 0:
                _user_id = RegisterUser(_user[0], _user[1], _user[2], _role)["id"]
            else:
                _user_id = _user_obj["id"]
            RegisterSession(_user_id, _auth_token, time() + 2*7*24*60*60, _hash)
            return json.dumps({"status": "OK", "message": "User registered"})
        except Exception as e:
            return json.dumps({"status": "ERR", "message": f"{e}"})


@app.route("/user/validate", methods=["POST"])
def validate():
    try:
        _json = request.data
        _json = json.loads(_json)

        _session_hash = _json["session_hash"]

        _data = GetAuthToken(_session_hash)
        if _data:
            _ret = {"auth_token": _data["auth_token"]}
            return json.dumps({"status": "OK", "message": _ret})
        else:
            return json.dumps({"status": "ERR", "message": "No such session"})
    except Exception as e:
        return json.dumps({"status": "ERR", "message": f"{e}"})


@app.route("/user/user", methods=["POST"])
def user():
    try:
        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _data = GetUserByToken(_hauth_token)
        if _data:
            return json.dumps({"status": "OK", "message": _data}, ensure_ascii=False).encode("utf8")
        else:
            return {"status": "ERR", "message": "Something went terribly wrong"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route("/user/logout", methods=["DELETE"])
def logout():
    try:
        _json = request.data
        _json = json.loads(_json)

        _hauth_token = _json["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        Logout(_hauth_token)
        return {"status": "OK", "message": "Logged out successfully"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


# @app.route("/user/delete", methods=["DELETE"])
# def delete_user():
#     try:
#         _json = request.json
#         _id = _json["id"]
#         _token = _json["token"]
#
#         _data = GetUserInfoId(_id)
#
#         if len(_data) != 0:
#             if _data["token"] == _token:
#                 DeleteUser(_id)
#                 return {"status": "OK", "message": "User deleted"}
#             else:
#                 return {"status": "ERR", "message": "You are not authorised to make changes"}
#         else:
#             return {"status": "ERR", "message": "User not found"}
#     except Exception as e:
#         return {"status": "ERR", "message": e}
