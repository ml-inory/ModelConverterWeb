# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/12
Desc: main
"""
import os
from flask import Flask, render_template, Response
from flask_login import LoginManager, current_user, login_required
from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_user, logout_user
from elements.LoginForm import LoginForm
from werkzeug.utils import secure_filename
from db import *

# 上传文件路径
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'upload')

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

# 支持的输入格式
INPUT_FORMAT = ('mmdet', 'mmcls', 'onnx')
INPUT_FILE = {
    'mmdet': ('mmdet_config', 'mmdet_pth'),
    'mmcls': ('mmcls_config', 'mmcls_pth'),
    'onnx': ('onnx_file', )
}

DBUser.register(username='rzyang', password='123')



@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)

@app.route('/<weight_file>')
@login_required
def show_weight_file(weight_file):
    return render_template('index.html', username=current_user.username, weight_file=weight_file)

# 处理上传表单
# 返回dict或者None
# def parse_upload_form(request):
#     input_format = request.form['type']
#     if input_format not in INPUT_FORMAT:
#         return None
#
#     result = {}
#     result['input_format'] = input_format
#     if input_format == 'mmdet':
#         if

# 上传文件
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print(type(request.files))
        print(list(request.files.lists())[0])
        file_type = request.form['input_format']
        print(file_type)
        if 'onnx_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['onnx_file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            # return redirect(url_for('uploaded_file', filename=filename))
            return redirect(request.url)
    return redirect(request.url)

# 上传成功后的处理
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(os.path.basename(filename))
    return "success", 200
    # return redirect(url_for('show_weight_file', weight_file=filename))
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login/', methods=('GET', 'POST'))  # 登录
def login():
    form = LoginForm()
    emsg = None
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        # user_info = get_user(user_name)  # 从用户数据中查找用户记录
        user = DBUser.get_user_by_name(user_name)
        if user is None:
            emsg = "用户名或密码有误"
        else:
            # user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user)  # 创建用户 Session
                return redirect(request.args.get('next') or url_for('index'))
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
    logout_user()
    return redirect(url_for('login'))

@login_manager.user_loader  # 定义获取登录用户的方法
def load_user(user_id):
    return DBUser.get_user_by_id(int(user_id))

if __name__ == '__main__':
    app.run(debug=True, port=9394)
