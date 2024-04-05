
from flask import Flask, request, render_template, redirect, session, flash, url_for
from .constants import FILE_DIR

app = Flask(__name__, 
        template_folder="/QuestProj/Quest", 
        static_url_path="/static/", 
        static_folder=FILE_DIR)
app.secret_key = 'secretKey'
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route('/khan')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
