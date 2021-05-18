# -*- coding: utf-8 -*-
"""
Author: rzyang
Date: 2021/05/18
Desc: database
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 创建数据库
db = SQLAlchemy()

# 用户表模型
class DBUser(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    input_format = db.Column(db.String(16), unique=False, nullable=True)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

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

    def verify_password(self, password):
        return check_password_hash(self.password, password)

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