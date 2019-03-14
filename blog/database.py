from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from passlib.apps import custom_app_context as pwd_context

app = Flask(__name__)

baseDir = os.path.abspath(os.path.join(os.path.dirname('_file_'),'..'))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128),unique= True, nullable=False)
    email_id = db.Column(db.String(128),unique= True, nullable=False)
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean(), default=True)
    created_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def __init__(self, username, email_id):
        self.username = username
        self.email_id = email_id

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email_id,
            'active': self.active,
            'created_timestamp': self.created_timestamp,
            'modified_timestamp': self.modified_timestamp
        }
    
    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def verify_user(self, username):
        user_name = request.authorization.username
        is_user = (user_name == username)
        return is_user

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), unique= True)
    author = db.Column(db.String(100))
    body = db.Column(db.String(2000))
    created_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    article_url = db.Column(db.String(100),nullable=False ,unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref(
        "owner_article", foreign_keys=[user_id]))

    def __init__(self, title, body, author, article_url, user_id):
        self.title = title
        self.body = body
        self.article_url = article_url
        self.author = author
        self.user_id = user_id

    def to_json(self):
        return {
            'title': self.title,
            'author': self.author,
            'body': self.body,
            'article_url': self.article_url,
            'created_timestamp': self.created_timestamp
        }

    def to_json_data(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'body': self.body,
            'created_timestamp': self.created_timestamp,
            'modified_timestamp': self.modified_timestamp,
            'article_url': self.article_url,
            'user_id': self.user_id
        }

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String(500))
    created_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    owner = db.relationship("User", backref=db.backref(
        "owner_comment", foreign_keys=[owner_id]))

    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"))
    article = db.relationship("Article", backref=db.backref(
        "article_comment", foreign_keys=[article_id]))

    def __init__(self, body, article_id, owner_id):
        self.body = body
        self.article_id = article_id
        self.owner_id = owner_id

    def to_json(self):
        return {
            'comment_id': self.id,
            'body': self.body,
            'created_timestamp': self.created_timestamp,
            'owner' : "Anonymous Coward." if (self.owner_id == None) else db.session.query(User)
                .filter(User.id == self.owner_id).all()[0].username ,
            'article_id' : self.article_id
        }

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag = db.Column(db.String(100))
    article_url = db.Column(db.Integer, db.ForeignKey("articles.article_url"))
    article = db.relationship("Article", backref=db.backref(
        "article_tag", foreign_keys=[article_url]))

    def to_json(self):
        return {
            'tag': self.tag,
            'article_url': self.article_url
        }


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    db.session.commit()