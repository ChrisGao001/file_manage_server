#!/usr/bin/python
#coding:utf8

from flask import Flask, request, redirect, url_for,session
from flask import render_template,make_response
from flask import send_from_directory
import datetime
import os.path
import os

app = Flask(__name__)
tool_path = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(tool_path,"data/")
app.config['UPLOAD_FOLDER'] = data_path
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 7200

def is_login():
    rc = session.get("is_login")
    return rc == "true"

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("name", type=str, default=None) 
        password = request.form.get("password", type=str, default=None) 
        if name == "admin" and password == "123456":
           resp = make_response(render_template("index.html"))
           session["is_login"] = "true"
           print("set cookie")
           return resp
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/index')
def index():
    if not is_login():
        return redirect(url_for('login'))
    return render_template("index.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not is_login():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            target_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(target_filename):
                cur_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                name,ext = os.path.splitext(target_filename)
                backup_filename = name + "-" + cur_date + ext
                os.rename(target_filename, backup_filename)
            file.save(target_filename)
            return redirect(url_for('uploaded_file', filename=filename))
    else:
        return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not is_login():
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/list')
def user():
    if not is_login():
        return redirect(url_for('login'))
    items = get_file_list()
    return render_template("list.html", items=items)

def get_file_list():
    files = []
    for item in os.listdir(data_path):
        files.append(item)
    return files 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port= 6432)
