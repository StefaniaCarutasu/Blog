from typing import List, Dict
from flask import Flask, request, jsonify
import mysql.connector
import json

from flask_login import login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))

    active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def is_active(self):
        return self.active
    

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()


def list_comments() -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    # Join comments and posts tables to get comments with associated post information
    query = '''
    SELECT comments.id, comments.text, posts.title AS post_title
    FROM comments
    JOIN posts ON comments.post_id = posts.id
    '''
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def create_comment(text: str, post_id: int) -> None:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Insert comment with associated post id
    query = 'INSERT INTO comments (text, post_id) VALUES (%s, %s)'
    cursor.execute(query, (text, post_id))

    connection.commit()
    cursor.close()
    connection.close()


def list_comments_for_post(post_id: int) -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    # Modified query to select comments for a specific post_id
    query = '''
    SELECT comments.id, comments.text
    FROM comments
    WHERE comments.post_id = %s
    '''
    cursor.execute(query, (post_id,))
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


@app.route('/')
@login_required
def get_comments():
    return jsonify({'comments': list_comments()})


@app.route('/get_comments/<int:post_id>', methods=['GET'])
@login_required
def get_comments_for_post(post_id):
    comments = list_comments_for_post(post_id)
    return jsonify({'comments': comments})


@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    app.logger.info(f"Received POST request for adding comment to post_id {post_id}")

    if request.method == 'POST':
        data = request.get_json()
        app.logger.info(f"Received data: {data}")

        if 'text' in data:
            create_comment(data['text'], post_id)
            app.logger.info("Comment added successfully")
            return jsonify({'status': 'success', 'message': 'Comment added successfully'})
        else:
            app.logger.error("Text parameter is missing")
            return jsonify({'status': 'error', 'message': 'Text parameter is missing'})
    else:
        app.logger.error("Invalid request method")
        return jsonify({'status': 'error', 'message': 'Invalid request method'})
