from typing import List, Dict
from flask import Flask, request, jsonify
import mysql.connector
import json

app = Flask(__name__)


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

def list_comments(post_id: int) -> List[Dict]:
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


@app.route('/add_comment', methods=['POST'])
def add_comment():
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data and 'post_id' in data:
            create_comment(data['text'], data['post_id'])
            return jsonify({'status': 'success', 'message': 'Comment added successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Text or post_id parameter is missing'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request method'})


@app.route('/')
def get_comments():
    return jsonify({'comments': list_comments()})


@app.route('/get_comments/<int:post_id>', methods=['GET'])
def get_comments_for_post(post_id):
    comments = list_comments(post_id)
    return jsonify({'comments': comments})