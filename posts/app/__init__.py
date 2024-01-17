from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, current_user
from prometheus_flask_exporter import PrometheusMetrics

from app.models import Users, db
from app.helpers import create_post, list_posts, delete_post, get_comments_for_post, get_post_by_id

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "tO$&!|0wkamvVia0?n$NqIRVWOG"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:example@db:3306/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

metrics = PrometheusMetrics(app, group_by='endpoint')
common_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

total_posts_created_counter = metrics.counter(
    'total_posts_created', 'Total number of posts created'
)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/add_post', methods=('GET', 'POST'))
@login_required
@total_posts_created_counter
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


total_calls_list = metrics.counter(
     'get_posts_count', 'Number of calls for get all posts'
)


@app.route('/')
@total_calls_list
def get_posts():
    return render_template('index.html', posts=list_posts(), user=current_user)


post_deletion_counter = metrics.counter(
    'post_deletion_count', 'Number of post deletions'
)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
@post_deletion_counter
def delete_post_route(post_id):
    if request.method == 'POST':
        delete_post(post_id)
        return render_template('index.html', posts=list_posts())
    else:
        return render_template('error.html', error='Invalid request method')


@app.route('/get_post/<int:post_id>', methods=['GET'])
@metrics.counter(
    'cnt_post', 'Number of invocations per post', labels={
        'post': lambda: request.view_args['post_id'],
        'status': lambda resp: resp.status_code
    })
def get_post(post_id):
    post = get_post_by_id(post_id)
    comments = get_comments_for_post(post_id)

    if post:
        return render_template('details.html', post=post, comments=comments)
    else:
        return render_template('error.html', error='Post not found')
