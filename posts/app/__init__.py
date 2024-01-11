from typing import List, Dict
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)


def list_posts() -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    # Modified query to select id and title columns from the posts table
    cursor.execute('SELECT id, title FROM posts')
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return results


def create_post(title: str, content: str) -> None:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Modified query to insert title and content into the posts table
    query = 'INSERT INTO posts (title, content) VALUES (%s, %s)'
    cursor.execute(query, (title, content))
    connection.commit()
    cursor.close()
    connection.close()


@app.route('/add_post', methods=['POST'])
def add_post():
    if request.method == 'POST':
        data = request.get_json()
        if 'title' in data and 'content' in data:
            create_post(data['title'], data['content'])
            return jsonify({'status': 'success', 'message': 'Post added successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Title or content parameter is missing'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request method'})


@app.route('/')
def get_posts():
    return jsonify({'posts': list_posts()})
