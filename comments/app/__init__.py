from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, UserMixin, current_user
from prometheus_flask_exporter import PrometheusMetrics
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "tO$&!|0wkamvVia0?n$NqIRVWOG"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
metrics = PrometheusMetrics(app, group_by='endpoint')
common_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

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


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Posts', backref='comments')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='comments')


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='posts')


def list_comments() -> list:
    comments = Comments.query.join(Posts).add_columns(Comments.id, Comments.text, Posts.title.label('post_title')).all()
    results = [{'id': comment.id, 'text': comment.text, 'post_title': comment.post_title} for comment in comments]
    return results


def create_comment(text: str, post_id: int) -> None:
    user_id = current_user.id if current_user.is_authenticated else None
    comment = Comments(text=text, post_id=post_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()


def list_comments_for_post(post_id: int) -> list:
    comments = Comments.query.filter_by(post_id=post_id).join(Users).add_columns(Comments.id, Comments.text, Users.username).all()
    results = [{'id': comment.id, 'text': comment.text, 'user': comment.username} for comment in comments]
    return results


@app.route('/')
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

