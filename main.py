# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/12
Desc: main
"""
import os
from flask import Flask, render_template, Response, session
from flask_login import LoginManager, current_user, login_required
from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_user, logout_user
from elements.LoginForm import LoginForm
from werkzeug.utils import secure_filename
from db import *

# 上传文件路径
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'input')

# 创建Flask应用
app = Flask(__name__)
# 设置表单交互密钥，防跨域攻击
app.secret_key = 'whale'
# 设置上传文件路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 初始化数据库
db = init_db('users', app)

# 实例化登录管理对象
login_manager = LoginManager()
# # 初始化应用
login_manager.init_app(app)
login_manager.login_view = 'login'

# 初始用户数据
INITIAL_USER_DATA = {
    'input_format': 'mmdet',
    'output_format': 'nnie',
    'output_name': '',

    # nnie参数
    'rgb_order': 'RGB',
    'nnie_input_width': 640,
    'nnie_input_height': 480,
}
# 用户数据
USER_DATA = {}

DBUser.register(username='rzyang', password='123')
DBUser.register(username='admin', password='123')

def init_user_data():
    username = current_user.username
    session['username'] = username
    session['data'] = INITIAL_USER_DATA

def current_user_data():
    return session['data']

@app.route('/')
@login_required
def index():
    if current_user.username not in session.keys():
        init_user_data()
    return render_template('index.html', username=current_user.username, **current_user_data())

# 处理GET/POST请求
@app.route('/', methods=['GET', 'POST'])
@login_required
def process_form():
    if request.method == 'POST':
        form_keys = request.form.keys()
        user_data = current_user_data()
        for k in form_keys:
            user_data[k] = request.form[k]
        for k in request.files:
            file = request.files[k]
            if file:
                filename = secure_filename(file.filename)
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], session['username']), exist_ok=True)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], session['username'], filename)
                file.save(save_path)
                user_data[k] = filename
                # 自动设置输出名称
                if user_data['output_name'] == '':
                    user_data['output_name'] = filename.split('.')[0]

        session['data'] = user_data
        print(session)

        return render_template('index.html', username=current_user.username, **current_user_data())
    return redirect(request.url)

@app.route('/login/', methods=('GET', 'POST'))  # 登录
def login():
    form = LoginForm()
    emsg = None
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user = DBUser.get_user_by_name(user_name)
        if user is None:
            emsg = "用户名或密码有误"
        else:
            if user.verify_password(password):  # 校验密码
                user.authenticated = True
                user.refresh_session() # 刷新session，以禁止多地登录
                db.session.add(user)
                db.session.commit()
                if login_user(user):  # 创建用户 Session
                    # print('Login Success,    ', current_user.username)
                    init_user_data()
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    return render_template('login.html', form=form, emsg=emsg)
            else:
                emsg = "用户名或密码有误"
    return render_template('login.html', form=form, emsg=emsg)

@app.route('/logout') # 登出
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    session.clear()
    logout_user()
    return redirect(url_for('login'))

@login_manager.user_loader  # 定义获取登录用户的方法
def load_user(session_token):
    return DBUser.query.filter_by(session_token=session_token).first()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=9394)
