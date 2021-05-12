# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/12
Desc: main
"""
from flask import Flask, render_template
from flask_login import LoginManager, current_user, login_required
from user import User, get_user
from flask import render_template, redirect, url_for, request
from flask_login import login_user
from elements.LoginForm import LoginForm

# 创建Flask应用
app = Flask(__name__)
# 设置表单交互密钥，防跨域攻击
app.secret_key = 'whale'

# 实例化登录管理对象
login_manager = LoginManager()
# # 初始化应用
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login/', methods=('GET', 'POST'))  # 登录
def login():
    form = LoginForm()
    emsg = None
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_info = get_user(user_name)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名或密码密码有误"
        else:
            user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                login_user(user)  # 创建用户 Session
                return redirect(request.args.get('next') or url_for('index'))
            else:
                emsg = "用户名或密码密码有误"
    return render_template('login.html', form=form, emsg=emsg)

@login_manager.user_loader  # 定义获取登录用户的方法
def load_user(user_id):
    return User.get(user_id)

if __name__ == '__main__':
    app.run(debug=True, port=9394)
