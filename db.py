# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/18
Desc: database
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
import os

# 创建数据库
db = SQLAlchemy()

# 用户表模型
class DBUser(db.Model):

    __tablename__ = 'user'

    TOKEN_LENGTH = 24

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String())
    refresh_token = db.Column(db.String())
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return str(self.access_token)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def register(username, password):
        if DBUser.get_user_by_name(username) is not None:
            return False
        new_user = DBUser(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return True

    @staticmethod
    def get_user_by_id(user_id):
        return DBUser.query.get(int(user_id))

    @staticmethod
    def get_user_by_name(username):
        return DBUser.query.filter_by(username=username).first()

    def refresh_token(self):
        identity = get_jwt_identity()
        self.access_token = create_access_token(identity=identity, fresh=False)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def create_token(self):
        self.access_token = create_access_token(identity=self.username, fresh=True)
        self.refresh_token = create_refresh_token(identity=self.username)

    def clear_token(self):
        self.access_token = ''
        self.refresh_token = ''

    def login(self, password):
        if not self.verify_password(password):
            return False
        self.create_token()
        self.authenticated = True
        db.session.add(self)
        db.session.commit()
        return True

    def logout(self):
        self.clear_token()
        self.authenticated = False
        db.session.add(self)
        db.session.commit()

# 历史记录表模型
class DBHistory(db.Model):

    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    username = db.Column(db.String(80))
    input_format = db.Column(db.String(16))
    input_files = db.Column(db.PickleType())
    output_format = db.Column(db.String(16))
    output_files = db.Column(db.PickleType())

# 初始化数据库
def init_db(db_name, app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/{}.db'.format(db_name)
    db.init_app(app)
    app.app_context().push()
    with app.app_context():
        db.create_all()
    return db