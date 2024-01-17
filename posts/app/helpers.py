from app.models import Posts, Users, Comments, db
from typing import List, Dict
from flask_login import login_required, LoginManager, current_user


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
