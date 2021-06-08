from flask import render_template, request, Blueprint
from silverhorse.models import Post
from flask_login import login_required
from flask_login import current_user

main = Blueprint('main', __name__)


# "@app.name...." is a python decorator which maps the view function to a route
@main.route("/home")
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(
    #     Post.date_posted.desc()).paginate(page=page, per_page=25)
    # posts = current_user.followed_posts().all()
    posts = current_user.followed_posts().paginate(page=page, per_page=1)
    # next_url = url_for('index', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('index', page=posts.prev_num) \
    #     if posts.has_prev else None
    return render_template('home.html', posts=posts, title='Home')


@main.route("/")
@main.route("/global")
def globals():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=1)
    return render_template('global.html', posts=posts, title="Global")


@main.route("/about")
def about():
    return render_template('about.html', title='About')
