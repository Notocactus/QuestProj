from flask import json
from .srv import app, session, redirect, request, render_template
from ..database import *
from time import time
from hashlib import md5



@app.route('/user/login', methods=["POST"])
def login_user():
    if request.method == 'POST':
        try:
            _time = str(time())
            _json = request.json()
            _timestamp = _json["timestamp"]
            _hash = _json["hash"]
            _user = _json["data"]["user"].split(' ')
            _role = _json["data"]["role"]
            _token = _json["data"]["token"]
            _nonce = _json["data"]["nonce"]
            _header = request.headers
            _hauth_token = _header["hauth_token"]

            # validate the received values
            if _hauth_token != _token:
                return {"status": "ERR", "message": "Unauthorized request"}

            _auth_token = md5(_token + _hash + _time)

            _user = GetUserByInfo(_user[0], _user[1], _user[2])
            if not _user:
                _user_id = RegisterUser(_user[0], _user[1], _user[2])
                RegisterSession(_user_id, _auth_token, time() + 2*7*24*60*60, _hash)
            else:
                RegisterSession(_user["id"], _auth_token, time() + 2*7*24*60*60, _hash)
            return {"status": "OK", "message": "User registered"}
        except Exception as e:
            return {"status": "ERR", "message": f"{e}"}


@app.route('/user/validate', methods=["POST"])
def validate():
    try:
        _json = request.json()
        _session_hash = _json['session_hash']

        _data = GetAuthToken(_session_hash)
        _ret = {"auth_token": _data["auth_token"]}
        if _data:
            return {"status": "OK", "message": json.dumps(_data)}
        else:
            return {"status": "ERR", "message": "No such session"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}


@app.route('/user/user', methods=["GET"])
def user():
    try:
        _header = request.headers
        _hauth_token = _header["auth_token"]
        if TokenExpired(_hauth_token):
            return {"status": "ERR", "message": "Registrate first"}

        _data = GetUserByToken(_hauth_token)
        if _data:
            return {"status": "OK", "message": json.dumps(_data)}
        else:
            return {"status": "ERR", "message": "Something went terribly wrong"}
    except Exception as e:
        return {"status": "ERR", "message": f"{e}"}



# @app.route('/user/delete', methods=["DELETE"])
# def delete_user():
#     try:
#         _json = request.json
#         _id = _json['id']
#         _token = _json['token']
#
#         _data = GetUserInfoId(_id)
#
#         if len(_data) != 0:
#             if _data['token'] == _token:
#                 DeleteUser(_id)
#                 return {"status": "OK", "message": "User deleted"}
#             else:
#                 return {"status": "ERR", "message": "You are not authorised to make changes"}
#         else:
#             return {"status": "ERR", "message": "User not found"}
#     except Exception as e:
#         return {"status": "ERR", "message": e}

