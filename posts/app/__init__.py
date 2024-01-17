from typing import List, Dict
from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, current_user
from flask_login import UserMixin

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "tO$&!|0wkamvVia0?n$NqIRVWOG"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


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
    return Users.query.get(user_id)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='posts')


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Posts', backref='comments')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='comments')


def get_post_by_id(post_id: int) -> Dict:
    post = Posts.query.filter_by(id=post_id).join(Users).add_columns(Posts.id, Posts.title, Posts.content,
                                                                     Users.username).first()
    if post:
        return {'id': post.id, 'title': post.title, 'content': post.content, 'username': post.username}
    return None


def get_comments_for_post(post_id: int) -> List[Dict]:
    comments = Comments.query.filter_by(post_id=post_id).join(Users).add_columns(Comments.id, Comments.text,
                                                                                 Users.username).all()
    return [{'id': comment.id, 'text': comment.text, 'username': comment.username} for comment in comments]


def get_comment_count(post_id):
    comment_count = db.session.query(db.func.count(Comments.id)) \
        .filter(Comments.post_id == post_id) \
        .scalar()
    return comment_count


def list_posts() -> List[Dict]:
    posts = Posts.query \
        .join(Users) \
        .add_columns(Posts.id, Posts.title, Users.username) \
        .all()

    result = [
                 {
                     'id': post.id,
                     'title': post.title,
                     'username': post.username,
                     'comment_count': get_comment_count(post.id)
                 }
                 for post in posts
             ][::-1]

    return result


def list_comments_for_post(post_id: int) -> List[Dict]:
    comments = Comments.query.filter_by(post_id=post_id).all()
    return [{'id': comment.id, 'text': comment.text} for comment in comments]


def create_post(title: str, content: str) -> None:
    user_id = current_user.id if current_user.is_authenticated else None
    new_post = Posts(title=title, content=content, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()


def delete_post(post_id: int) -> None:
    comments = Comments.query.filter_by(post_id=post_id).all()
    for comment in comments:
        db.session.delete(comment)

    post = Posts.query.filter_by(id=post_id).first()
    if post:
        db.session.delete(post)

    db.session.commit()


@app.route('/add_post', methods=('GET', 'POST'))
@login_required
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
    return render_template('index.html', posts=list_posts(), user=current_user)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post_route(post_id):
    if request.method == 'POST':
        delete_post(post_id)
        return render_template('index.html', posts=list_posts())
    else:
        return render_template('error.html', error='Invalid request method')


@app.route('/get_post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = get_post_by_id(post_id)
    comments = get_comments_for_post(post_id)

    if post:
        return render_template('details.html', post=post, comments=comments)
    else:
        return render_template('error.html', error='Post not found')
