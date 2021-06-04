# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/12
Desc: main
"""
import os
from flask import Flask, render_template, Response, session, redirect, url_for, request, flash, send_from_directory, jsonify, make_response, send_file
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_restful import Resource, Api, reqparse
from elements.LoginForm import LoginForm
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies)
from flask_cors import CORS
from db import *
from err import *
# from celery import Celery
from celery.result import AsyncResult
from converter import Converter
import redis
from datetime import datetime
from tasks import cel, convert_model, TaskMonitor


# 支持的输入格式
SUPPORTED_INPUT_FORMAT = ('mmdet', 'mmcls', 'onnx')
# 支持的输出格式
SUPPORTED_OUTPUT_FORMAT = ('nnie', 'onnx', 'tengine')

# 上传文件路径
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'input')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'output')

# 创建Flask应用
app = Flask(__name__)
# 设置表单交互密钥，防跨域攻击
app.secret_key = 'w03ic03h982307ca9385l8c8de19'
# 设置上传文件路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

api = Api(app)
# 初始化数据库
db = init_db('users', app)
# 初始化jwt
app.config['JWT_SECRET_KEY'] = 'wf45ww4h64wefa64cxeql64weec64'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['JWT_SESSION_COOKIE'] = True
jwt = JWTManager(app)
# 初始化login
app.config['REMEMBER_COOKIE_DURATION '] = timedelta(days=7)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# 配置Celery
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:9394'
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:9394'
# celery = make_celery(app)
# class ContextTask(celery.Task):
#     def __call__(self, *args, **kwargs):
#         with app.app_context():
#             return self.run(*args, **kwargs)

# celery.Task = ContextTask

# 跨域
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

API_VERSION = 'v1'
BASE_URL = '/api/' + API_VERSION

DBUser.register('rzyang', '123')


@login_manager.user_loader
def load_user(access_token):
    # print('access_token: ' + access_token)
    if access_token == '':
        return None
    return DBUser.query.filter_by(access_token=access_token).first()


# 创建返回信息
def msg(content):
    return jsonify(msg=content)

# /api
class MCApi(Resource):
    def get(self):
        return jsonify(version=API_VERSION)


# /login/:username/:password
class MCLogin(Resource):
    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', type=bool, default=False)
        # print(username, password, remember)
        # 检查参数完整性
        if (username is None or password is None) or username == '' or password == '':
            return make_response(msg('用户名或密码不能为空'), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        # 检查用户是否存在
        user = DBUser.get_user_by_name(username)
        if user is None:
            return make_response(msg('用户名或密码不正确'), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        # 验证密码
        if not user.login(password):
            return make_response(msg('用户名或密码不正确'), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        login_user(user, remember=remember, duration=app.config['REMEMBER_COOKIE_DURATION '])
        # 存储在session
        session['username'] = user.username
        session['access_token'] = user.access_token
        session['refresh_token'] = user.refresh_token
        # 计算token过期时间：当前时间+过期时长
        exp_timestamp = int((datetime.utcnow() + app.config["JWT_ACCESS_TOKEN_EXPIRES"]).timestamp())
        response = make_response(jsonify(msg='Login as {} success'.format(username),
                                     username=user.username,
                                     access_token=user.access_token,
                                     refresh_token=user.refresh_token,
                                     expiration=exp_timestamp), ERROR_CODE['SUCCESS'])
        # set_access_cookies(response, user.access_token)
        return response


# /token
class MCToken(Resource):
    @login_required
    @jwt_required(refresh=True)
    def get(self):
        user = DBUser.get_user_by_name(session['username'])
        if not user:
            return make_response(msg('user {} does NOT exist'.format(session['username'])), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        user.refresh_token()
        # 获取token过期时间
        exp_timestamp = int((datetime.utcnow() + app.config["JWT_ACCESS_TOKEN_EXPIRES"]).timestamp())
        return make_response(jsonify(msg='Refresh token success',
                                     access_token=user.access_token,
                                     expiration=exp_timestamp), ERROR_CODE['SUCCESS'])


# /logout
class MCLogout(Resource):
    @login_required
    @jwt_required()
    def post(self):
        # 检查用户是否存在
        username = session.get('username')
        user = DBUser.get_user_by_name(username)
        if user is None:
            return make_response(msg('user {} does NOT exist'.format(username)), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        if not user.is_authenticated():
            return make_response(msg('user {} is not login'.format(username)), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        user.logout()
        logout_user()
        session.clear()
        response = make_response(jsonify(msg='Logout {} success'.format(user.username)), ERROR_CODE['SUCCESS'])
        # unset_jwt_cookies(response)
        return response


# /input
class MCInput(Resource):
    @login_required
    @jwt_required()
    def post(self):
        username = session.get('username')
        input_format = request.form.get('format')
        config = request.files.get('config')
        weight = request.files.get('weight')
        if input_format not in SUPPORTED_INPUT_FORMAT:
            return make_response(jsonify(msg='format {} is not supported.Supported formats include {}'.format(input_format, SUPPORTED_INPUT_FORMAT)), 402)

        if input_format != 'onnx':
            if config is None:
                return make_response(jsonify(msg='未提供配置文件'), 402)
            config_filename = secure_filename(config.filename)
            if not config_filename.endswith('.json'):
                return make_response(jsonify(msg='config file must be json'), 402)
            config_path = os.path.join(app.config['UPLOAD_FOLDER'], username, config_filename)
            config.save(config_path)
            session['config_path'] = config_path
        else:
            session['config_path'] = ''

        if weight is None:
            return make_response(jsonify(msg='未提供权重文件'), 402)
        weight_filename = secure_filename(weight.filename)
        if input_format != 'onnx':
            if not weight_filename.endswith('.pth'):
                return make_response(jsonify(msg='weight file must be .pth file'), 402)
        else:
            if not weight_filename.endswith('.onnx'):
                return make_response(jsonify(msg='weight file must be .onnx file'), 402)
        weight_path = os.path.join(app.config['UPLOAD_FOLDER'], username, weight_filename)
        weight.save(weight_path)

        response = make_response(jsonify(msg='Set input success'), ERROR_CODE['SUCCESS'])

        session['input_format'] = input_format
        session['weight_path'] = weight_path

        return response


# /output
class MCOutput(Resource):
    @login_required
    @jwt_required()
    def post(self):
        output_format = request.form.get('format')
        output_name = request.form.get('name')
        if output_format is None or output_name is None:
            return make_response(jsonify(msg='Both format and name must be provided'), 402)
        if output_format not in SUPPORTED_OUTPUT_FORMAT:
            return make_response(jsonify(msg='format {} is not supported.Supported formats include {}'.format(output_format, SUPPORTED_OUTPUT_FORMAT)), 402)
        if not output_name or output_name == '':
            return make_response(jsonify(msg='未设置输出名称'), 402)

        session['output_format'] = output_format
        session['output_name'] = output_name

        return make_response(jsonify(msg='Set output success'), ERROR_CODE['SUCCESS'])


# /convert
class MCConvert(Resource):
    def check_params(self):
        params = ('input_format', 'weight_path')
        for k in params:
            # print(k + ': ' + session.get(k))
            if session.get(k) is None:
                return False, k
        return True, ''

    @login_required
    @jwt_required()
    def post(self):
        flag, key = self.check_params()
        if not flag:
            return make_response(jsonify(msg='{} is not set.Please make sure /input and /output is post correctly before calling /convert'.format(key)), 402)

        width = request.form.get('width', type=int, default=-1)
        height = request.form.get('height', type=int, default=-1)
        order = request.form.get('order', type=str, default='RGB')
        mean = request.form.get('mean', type=int, default=0)
        scale = request.form.get('scale', type=float, default=1.0)
        output_format = request.form.get('output_format', type=str)
        output_name = request.form.get('output_name', type=str)
        img_archive = request.files.get('img_archive')

        print('output_name:' + output_name)

        if output_format is None or output_name is None:
            return make_response(jsonify(msg='Both format and name must be provided'), 402)
        if output_format not in SUPPORTED_OUTPUT_FORMAT:
            return make_response(jsonify(msg='format {} is not supported.Supported formats include {}'.format(output_format, SUPPORTED_OUTPUT_FORMAT)), 402)
        if not output_name or output_name == '':
            return make_response(jsonify(msg='未设置输出名称'), 402)

        if output_format == 'nnie':
            if img_archive is None:
                return make_response(jsonify(msg='NNIE需要图片压缩包'), 402)
            else:
                # 保存压缩包
                archive_filename = secure_filename(img_archive)
                archive_save_path = os.path.join(app.config['UPLOAD_FOLDER'], session['username'], archive_filename)
                img_archive.save(archive_save_path)
                session['img_archive'] = archive_save_path

        # 保存转换参数
        cvt_params = {}
        for key in ('width', 'height', 'order', 'mean', 'scale', 'output_format', 'output_name'):
            cvt_params[key] = eval(key)
        for key in ('input_format', 'config_path', 'weight_path'):
            cvt_params[key] = session[key]
        cvt_params['username'] = session['username']
        now = datetime.now()
        cvt_params['date'] = now.strftime("%Y-%m-%d %H:%M:%S")

        # 新建celery任务
        try:
            convert_model.delay(cvt_params)
            # add.delay(4, 4)
            # print(result.get(timeout=10))
        except Exception as err:
            return make_response(jsonify(msg=str(err)), 500)

        return make_response(jsonify(msg='Post task of converting {} to {} success'.format(session['input_format'], output_format), date=cvt_params['date'], output_format=cvt_params['output_format'], output_name=cvt_params['output_name']), ERROR_CODE['SUCCESS'])


# /session
class MCGetSession(Resource):
    @login_required
    def get(self):
        return make_response(jsonify(**session), 200)

# /tasks
class MCTasks(Resource):
    @login_required
    @jwt_required()
    def get(self):
        tasks = TaskMonitor.query(session['username'])
        return make_response(jsonify(msg='Query success', tasks=tasks), 200)

# /model
class MCModel(Resource):
    @login_required
    @jwt_required()
    def get(self):
        index = request.args.get('index', type=int)
        ret = TaskMonitor.get_model(session['username'], index)
        msg = ret['msg']
        if msg == 'FAILED':
            return make_response(jsonify(msg=msg), 502)
        else:
            return make_response(jsonify(**ret), 200)

@login_required
@jwt_required()
@app.route('/download/<int:index>', methods=['GET', 'POST'])
def download(index):
    # index = request.args.get('index', type=int)
    print('download index: ', index)
    username = session['username']
    task = TaskMonitor.tasks[username][index]
    result = AsyncResult(id=task['task_id'], app=cel)
    model_path = result.get()['model_path']
    filename = os.path.basename(model_path)
    print('model_path: ' + model_path)
    print('filename:', filename)
    return send_from_directory(directory=os.path.join(app.config['DOWNLOAD_FOLDER'], session['username']), filename=filename, as_attachment=True)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return render_template('login.html', username=current_user.username, password=current_user.password, remember=True)
    else:
        return render_template('login.html')


@app.route('/index')
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)



if __name__ == '__main__':
    api.add_resource(MCApi, BASE_URL)
    api.add_resource(MCLogin, BASE_URL + '/login')
    api.add_resource(MCToken, BASE_URL + '/token')
    api.add_resource(MCLogout, BASE_URL + '/logout')
    api.add_resource(MCInput, BASE_URL + '/input')
    api.add_resource(MCOutput, BASE_URL + '/output')
    api.add_resource(MCConvert, BASE_URL + '/convert')
    api.add_resource(MCGetSession, BASE_URL + '/session')
    api.add_resource(MCTasks, BASE_URL + '/tasks')
    # api.add_resource(MCModel, BASE_URL + '/model')
    app.config['TESTING'] = False
    app.run(host="127.0.0.1", debug=True, port=4396)
