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
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM comments')
    results = [{id: text} for (id, text) in cursor]
    cursor.close()
    connection.close()

    return results


def create_comment(text: str) -> None:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('INSERT INTO comments (text) VALUES (%s)', (text,))
    connection.commit()
    cursor.close()
    connection.close()


@app.route('/add_comment', methods=['POST'])
def add_comment():
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data:
            create_comment(data['text'])
            return jsonify({'status': 'success', 'message': 'Comment added successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Text parameter is missing'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request method'})


@app.route('/')
def get_comments():
    return jsonify({'comments': list_comments()})
