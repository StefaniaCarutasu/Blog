from flask import Flask
from flask import (
    render_template, request, flash, redirect
)
from flask_sqlalchemy import SQLAlchemy

import logging

from flask_session import SqlAlchemySessionInterface
from app.extensions import db, sess, migrate

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "8AE5EF15A4BEA"


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)
        
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = "8AE5EF15A4BEA"

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'

    db = SQLAlchemy(app)

    with app.app_context():
         db.init_app(app)
         migrate.init_app(app, db)

         sess.init_app(app)
         SqlAlchemySessionInterface(app, db, "sessions", "sess_")


@app.route('/')
def auth_app():
    return app


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        app.logger.debug(data)
        flash(data)
        if 'username' in data and 'password' in data:
            if Users.query.filter_by(username=data['username']).first():
                return redirect('auth/error')
            else:
                user = Users(username=data["username"], password=data["password"])
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


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         if not request.is_json:
#             flash('Invalid request format', 'danger')
#             return redirect(request.url)

#         data = request.get_json()
#         if not data or not 'username' in data or not 'password' in data:
#             flash('Missing required fields', 'danger')
#             return redirect(request.url)

#         username = data['username']
#         password = data['password']

#         user = Users.query.filter_by(username=username).first()
#         if not user:
#             flash('Incorrect username or password', 'danger')
#             return redirect('/login')

#         if not user.check_password(password):
#             flash('Incorrect username or password', 'danger')
#             return redirect('/login')

#         login_user(user)
#         flash('Logged in successfully', 'success')
#         return redirect('/')

#     return render_template('login.html')