from typing import List, Dict
from flask import Flask, request, jsonify, render_template, url_for
import mysql.connector
from werkzeug.utils import redirect


app = Flask(__name__, template_folder='templates', static_folder='static')


def get_post_by_id(post_id: int) -> Dict:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    # Query to select a post by its ID
    query = 'SELECT id, title, content FROM posts WHERE id = %s'
    cursor.execute(query, (post_id,))
    post = cursor.fetchone()

    cursor.close()
    connection.close()

    return post


def get_comments_for_post(post_id: int) -> List[Dict]:
    comments = list_comments_for_post(post_id)
    return comments


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
    results = cursor.fetchall()[::-1]
    cursor.close()
    connection.close()

    return results


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


def delete_post(post_id: int) -> None:
    config = {
        'user': 'root',
        'password': 'example',
        'host': 'db',
        'port': '3306',
        'database': 'blog'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Delete comments associated with the post
    cursor.execute('DELETE FROM comments WHERE post_id = %s', (post_id,))

    # Delete the post
    cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))

    connection.commit()
    cursor.close()
    connection.close()


@app.route('/add_post', methods=('GET', 'POST'))
def add_post():
    if request.method == 'POST':
        data = request.get_json()
        if 'title' in data and 'content' in data:
            create_post(data['title'], data['content'])
            return render_template('index.html', posts=list_posts())
        else:
            return render_template('error.html', error='Invalid data')
    else:
        return render_template('create.html')


@app.route('/')
def get_posts():
    return render_template('index.html', posts=list_posts())


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post_route(post_id):
    if request.method == 'POST':
        # Delete the post and its comments
        delete_post(post_id)
        # Redirect to the updated posts page
        return render_template('index.html', posts=list_posts())
    else:
        # Handle invalid request method
        return render_template('error.html', error='Invalid request method')


@app.route('/get_post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = get_post_by_id(post_id)
    comments = get_comments_for_post(post_id)

    if post:
        return render_template('details.html', post=post, comments=comments)
    else:
        return render_template('error.html', error='Post not found')
