import time
import os
import json
from hashlib import md5
from datetime import datetime,date
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack,jsonify
from models import db, User, Chatroom, Message

app = Flask(__name__)

SECRET_KEY = 'secretkey'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'p3.db')

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True 

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

def get_user_id(username):
	temp = User.query.filter_by(username=username).first()
	return temp.id if temp else None
def get_room_id(name):
	temp = Chatroom.query.filter_by(name=name).first()
	return temp.id if temp else None

@app.before_request
def before_request():
	g.user = None
	if 'id' in session:
		g.user = User.query.filter_by(id=session['id']).first()

@app.route('/')
def root():
		return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():

	if g.user:
		return redirect(url_for('controller'))
	error = None
	if request.method == 'POST':
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not user.password == request.form['password']:
			error = 'Invalid password'
		else:
			flash('Logged in successfully!')
			session['id'] = user.id
			return  redirect(url_for('controller'))		
	return render_template('login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def register():
	#if g.user:
		#return redirect(url_for('root'))
	error = None
	if request.method == 'POST':
		if not request.form['username']: 
			error = 'Username feild is empty'
		elif not request.form['password']:
			error = 'Password feild is empty'
		elif get_user_id(request.form['username']) is not None:
			error = 'This username already exists! Please choose different one'
		else:
			input_username = request.form['username']
			input_password = request.form['password']
			new_user = User(username=input_username,password=input_password)
			db.session.add(new_user)
			db.session.commit()
			flash('Registeration is complete')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

@app.route('/home', methods=['GET', 'POST'])
def controller():
	if request.method == 'POST':
			db.session.delete(Chatroom.query.filter_by(id=request.form['delBtn']).first())
			db.session.commit()	
			flash('deleted successfully')
	return render_template('chatroomList.html', rooms=Chatroom.query.all())

@app.route('/rooms/<title>', methods=['GET', 'POST'])
def rooms(title):
	room = Chatroom.query.filter_by(name=title).first()
	if session.get('room_id'):
		if session['room_id'] == room.id or 	session['room_id'] == None:
			chat = Message.query.filter(Message.room_id==session['room_id']).all()
			return render_template('rooms.html',chat=chat, chatroom=title)
		else:
			current = Chatroom.query.filter_by(id=session['room_id']).first()
			flash('You have to exit room before joining other rooms')
			return redirect(url_for('rooms', title=current.name))
	else:
		session['room_id'] = room.id
		chat = Message.query.filter(Message.room_id==session['room_id']).all()
		return render_template('rooms.html',chat=chat ,chatroom=title)

@app.route('/post', methods=['POST'])
def post():
	text = request.json
	user = User.query.filter_by(id=session['id']).first()
	msg = Message(message=text['msg'], date=datetime.now(), author_id=session['id'], room_id=session['room_id'], sentBy=user.username)
	db.session.add(msg)
	db.session.commit()
	return render_template('rooms.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		user = User.query.filter_by(id=session['id']).first()
		chatroom = get_room_id(request.form['room'])
		if chatroom is not None:
			flash('this name already exists! Please choose different one') 
		else:
			chatroom = Chatroom(name=request.form['room'], host_id=session['id'])
			db.session.add(chatroom)
			db.session.commit()
			flash('Your chatroom is created successfully!')
			return redirect(url_for('controller'))
	return render_template('create.html')

@app.route('/logout')
def logout():
	flash('You were logged out')
	session.pop('id', None)
	return redirect(url_for('login'))

@app.route('/exit', methods=['GET', 'POST'])
def exit():
	session.pop('room_id', None)
	return redirect(url_for('controller'))
	
@app.route('/show_msg', methods=['GET'])
def show_msg():
	if Chatroom.query.filter_by(id=session['room_id']).first():
		return dumps(Message.query.with_entities(Message.message, Message.author_id).filter((Message.room_id==session['room_id']) & (Message.date, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))).all())
	else:
		session.pop('room_id', None)
		return flash('ali test')
