from flask import Flask
from flask import (
    render_template, request, flash, redirect, url_for
)

from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import UserMixin
import logging

from flask_session import SqlAlchemySessionInterface
# from app.extensions import db, sess, migrate
from flask_login import LoginManager, login_user, logout_user, login_required

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "tO$&!|0wkamvVia0?n$NqIRVWOG"


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'

db = SQLAlchemy(app)
# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app) 
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

    active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def is_active(self):
        return self.active
    
class RegisterForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(0,50)])
    password =  PasswordField("Password:", validators=[Length(min=8, message='Too short')])
    repeatPassword =  PasswordField("Repeat password", validators=[Length(min=8, message='Too short')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(0,50)])
    password =  PasswordField(validators=[Length(min=8, message='Too short')])
    submit = SubmitField('Register')
    

@app.route('/')
def auth_app():
    return app

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()
    
@app.route("/error", methods=['GET'])
def error():
    return render_template('error.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    form = RegisterForm()
        
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        repeatPassword = form.repeatPassword.data
        if password != repeatPassword:
            message = "Passwords must match!"
        else:
            if Users.query.filter_by(username=username).first():
                message = "Username already exists!"
            else:
                hash_pass = bcrypt.generate_password_hash(password)
                user = Users(username=username, password=hash_pass)
                db.session.add(user)
                db.session.commit()

                user = Users.query.filter_by(username=username).first()
                login_user(user)
                    
                return redirect('/posts')
    
    return render_template('register.html', form=form, message=message)

@app.route('/login', methods=['GET','POST'])
def login():
    message=''
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Users.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(password=password, pw_hash=user.password):
                login_user(user)
                return redirect('/posts')
            else:
                message = 'Password not valid!'    
        else:
            message = 'There is no user with this username!'    

    return render_template('login.html', form=form, message=message)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/auth/login')

