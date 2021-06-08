from PIL.Image import NONE
from flask import render_template, session, url_for, flash, redirect, request, Blueprint, g
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from silverhorse import db, bcrypt, oauth
from silverhorse.models import User, Post
from silverhorse.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                     RequestResetForm, ResetPasswordForm)
from silverhorse.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_email = User.query.filter_by(
            email=form.login_creadential.data).first()
        user_username = User.query.filter_by(
            username=form.login_creadential.data).first()
        user = None
        if user_email:
            user = user_email
        if user_username:
            user = user_username
        if user is None:
            flash('Login Unsuccessful. Please check email or username', 'danger')
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You are logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(
                'Login Unsuccessful. Please check password', 'danger')
    return render_template('login_test.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


# setting up g.user global veriable
@users.before_request
def before_request():
    g.user = current_user


@users.route("/user/<string:username>")
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user.html', posts=posts, user=user, username=username)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


#google login##############
# oauth setup
google = oauth.register(
    name="google",
    # client_id=os.getenv("GOOGLE_CLIENT_ID"),
    # client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_id="517642626732-8i4m3ve7k3804er13ma84h0tcvni4i7q.apps.googleusercontent.com",
    client_secret="qvu6v7gyUXFugJwPlytCe6RA",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    # This is only needed if using openId to fetch user info
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={"scope": "openid email profile"},
)


@users.route("/login_google")
def login_google():
    google = oauth.create_client("google")  # create the google oauth client
    redirect_uri = url_for("users.authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


@users.route("/authorize")
def authorize():
    google = oauth.create_client("google")  # create the google oauth client
    token = (
        google.authorize_access_token()
    )  # Access token from google (needed to get user info)
    # userinfo contains stuff u specificed in the scrope
    resp = google.get("userinfo")
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session["profile"] = user_info
    # make the session permanant so it keeps existing after broweser gets closed
    session.permanent = True
    return redirect("/")
###########################


#follow and unfollow routes(views functions)#########################
@users.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('main.home'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('users.user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('users.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!', 'success')
    return redirect(url_for('users.user', username=username))


@users.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('main.home'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('users.user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('users.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.', 'success')
    return redirect(url_for('users.user', username=username))
#####################################################################
