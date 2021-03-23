from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATION']= False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///p3.db'
db = SQLAlchemy(app)

class User(db.Model):
	"""docstring for User"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100),nullable=False)
	password = db.Column(db.String(100),nullable=False)
def __init__(self, username, password):
	self.username = username
	self.password  = password

def __repr__(self):
	return '<User {}>'.format(self.username)

class Chatroom(db.Model):
	"""docstring for Chatroom"""
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
    #1-M chatroom created by
	host_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #1-M print all messages with this chatroom id 
	msg = db.relationship('Message', backref='chat', lazy='dynamic')

def __init__(self, name,msg):
	self.name = name
	self.msg = msg


class Message(db.Model):
	"""docstring for Message"""
	id = db.Column(db.Integer, primary_key=True)
	message = db.Column(db.String(500), nullable=False)
	date = db.Column(db.DateTime(), nullable=False)
	sentBy = db.Column(db.String(50), nullable=False) 
    #1-M with user --- message typed by
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #1-M with chatroom --- what chatroom this message was written in
	room_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'))

def __init__(self, message,date,author_id,room_id):
	self.message = message
	self.date=date
	self.author_id=author_id
	self.room_id=room_id

		