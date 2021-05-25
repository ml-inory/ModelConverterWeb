# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/12
Desc: main
"""
import os
from flask import Flask, render_template, Response, session, redirect, url_for, request, flash, send_from_directory, jsonify, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_restful import Resource, Api, reqparse
from elements.LoginForm import LoginForm
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies)
from db import *
from err import *

# 上传文件路径
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'input')

# 创建Flask应用
app = Flask(__name__)
# 设置表单交互密钥，防跨域攻击
app.secret_key = 'w03ic03h982307ca9385l8c8de19'
# 设置上传文件路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

api = Api(app)
# 初始化数据库
db = init_db('users', app)
# 初始化jwt
app.config['JWT_SECRET_KEY'] = 'wf45ww4h64wefa64cxeql64weec64'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)
# 初始化login
login_manager = LoginManager()
login_manager.init_app(app)

API_VERSION = 'v1'
BASE_URL = '/api/' + API_VERSION

DBUser.register('rzyang', '123')


@login_manager.user_loader
def load_user(access_token):
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
        # 检查参数完整性
        if username is None or password is None:
            return make_response(msg('username and password must be provided'), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        # 检查用户是否存在
        user = DBUser.get_user_by_name(username)
        if user is None:
            return make_response(msg('user {} does NOT exist'.format(username)), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        # 验证密码
        if not user.login(password):
            return make_response(msg('password is not correct'), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        login_user(user)
        # 存储在session
        session['username'] = user.username
        # 计算token过期时间：当前时间+过期时长
        exp_timestamp = int((datetime.utcnow() + app.config["JWT_ACCESS_TOKEN_EXPIRES"]).timestamp())
        response = make_response(jsonify(msg='Login as {} success'.format(username),
                                     access_token=user.access_token,
                                     refresh_token=user.refresh_token,
                                     expiration=exp_timestamp), ERROR_CODE['SUCCESS'])
        set_access_cookies(response, user.access_token)
        return response


# /token?username=
class MCToken(Resource):
    @login_required
    @jwt_required(refresh=True)
    def get(self):
        # username = request.args.get('username', type=str, default=None)
        # if not username:
        #     return make_response(msg('username must be provided'), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        # if username != session.get('username'):
        #     return make_response(msg('user {} is not login'.format(username)), ERROR_CODE['INVALID_UNAME_OR_PWD'])
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
        # username = request.form.get('username')
        # if username != session.get('username'):
        #     return make_response(msg('{} is not login'.format(username)), 401)
        # 检查用户是否存在
        username = session.get('username')
        user = DBUser.get_user_by_name(username)
        if user is None:
            return make_response(msg('user {} does NOT exist'.format(username)), ERROR_CODE['INVALID_UNAME_OR_PWD'])
        user.logout()
        logout_user()
        session.pop('username', None)
        response = make_response(jsonify(msg='Logout {} success'.format(user.username)), ERROR_CODE['SUCCESS'])
        unset_jwt_cookies(response)
        return response


api.add_resource(MCApi, BASE_URL)
api.add_resource(MCLogin, BASE_URL + '/login')
api.add_resource(MCToken, BASE_URL + '/token')
api.add_resource(MCLogout, BASE_URL + '/logout')

if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True, port=4396)
