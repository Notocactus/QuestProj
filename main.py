# import pymysql
# import flask
import datetime

from db._db_config import engine
# from db_config import mysql
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash

from db._primitive import *


# _password = "0hN0oo..."
# _name = "Nabstablook"
# _email = "NBlooky@mail.ru"
#
# _data = select(engine, "users")
# print(_data)

# _hashed_password = generate_password_hash(_password)
# date = datetime.datetime.now()
# _id = int(f"{date.year}{date.month}{date.day}{date.hour}"
#           f"{date.minute}{date.second}{date.microsecond}")
#
# # save edits
# columns = ['id', 'login', 'user_name', 'password_hash']
# values = [_id, _email, _name, _hashed_password]
# insert(engine, "users", columns, values)

# date = datetime.datetime.now()
# id = int(f"{date.year}{date.month}{date.day}{date.hour}{date.minute}{date.second}{date.microsecond}")
# print(id)


# _data = select(engine, "users", 'id', 'login', 'password_hash', login=_email)
# if len(_data) != 0:
#     if check_password_hash(_data[0]['password_hash'], _password):
#         print(_data)
#     else:
#         print(":(")

# from flask import Flask, request
# from Quest import app
#
#
# # app = Flask(__name__)
#
#
# @app.route('/khan')
# def hello_world():
#     return 'Welcome!'
#
#
# if __name__ == '__main__':
#     app.run()

