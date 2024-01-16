from flask import Flask
from flask import (
    render_template, request, flash, redirect
)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import UserMixin
import logging

from flask_session import SqlAlchemySessionInterface
# from app.extensions import db, sess, migrate
from flask_login import LoginManager, login_user

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "8AE5EF15A4BEA"


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'

db = SQLAlchemy(app)
# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app) 

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

    active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def is_active(self):
        return self.active
    

@app.route('/')
def auth_app():
    return app

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        app.logger.debug(data)
        flash(data)
        if 'username' in data and 'password' in data and 'confirmPassword' in data:
            if data['password'] != data['confirmPassword']:
                return('register.html')
            if Users.query.filter_by(username=data['username']).first():
                return redirect('auth/error')
            else:
                hash_pass = bcrypt.generate_password_hash(data["password"])
                user = Users(username=data["username"], password=hash_pass)
                db.session.add(user)
                db.session.commit()
                return redirect('/posts')
        else:
            return render_template("register.html")
    else:
        return render_template("register.html")
    
@app.route("/error", methods=['GET'])
def error():
    return render_template('error.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.is_json:
            flash('Invalid request format', 'danger')
            return redirect(request.url)

        data = request.get_json()
        if not data or not 'username' in data or not 'password' in data:
            flash('Missing required fields', 'danger')
            return redirect(request.url)

        username = data['username']
        password = data['password']

        user = Users.query.filter_by(username=username).first()
        if not user:
            flash('Incorrect username or password', 'danger')
            return redirect('/auth/login')

        if not bcrypt.check_password_hash(user.password, password):
            flash('Incorrect username or password', 'danger')
            return redirect('/auth/login')

        login_user(user)
        flash('Logged in successfully', 'success')
        return redirect('/posts')

    return render_template('login.html')

