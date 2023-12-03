from flask import Blueprint

from flask import render_template, url_for, flash, redirect, request, abort
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ChangePasswordForm, ChangePasswordManuallyForm
from .. import db, bcrypt, mail
from ..models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from .utils import save_picture, send_reset_email

users = Blueprint('users', __name__)




@users.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user1 = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user1)
        db.session.commit()
        flash('Account created. You can sign in now.', 'success')
        return redirect(url_for('users.login'))

    return render_template('main/register.html', title='Register', form=form)


@users.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Successfully Logged in {form.username.data}', 'success')
            return redirect(url_for('main.home'))
        elif not user:
            flash('Login Failed. Check your username', 'danger')
        elif not bcrypt.check_password_hash(user.password, form.password.data):
            flash('Login Failed. Check your password', 'danger')

    return render_template('main/login.html', title='Login', form=form)

@users.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
    user = User.query.get_or_404(current_user.id)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account info updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('main/account.html', title='Account', image_file=image_file, form=form, user=user)


@users.route('/user/<int:user_id>')
def userview(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date_posted.desc()).paginate(per_page=6, page=page)
    return render_template('main/user.html', posts=posts, user=user)


@users.route('/account/img_reset', methods=['POST'])
@login_required
def img_reset():
    user = User.query.get_or_404(current_user.id)

    picture_file = url_for('static', filename='default.jpg')
    current_user.image_file = picture_file
    db.session.commit()
    flash('Image has been reset', 'success')
    return redirect(url_for('users.account'))


@users.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Check your email inbox', 'info')
        return redirect(url_for('users.login'))
    return render_template('main/reset_request.html', title='Reset Password', form=form)



@users.route('/reset_request/<token>', methods=['GET', 'POST'])
def change_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid token', 'danger')
        return redirect(url_for('users.reset_request'))
    form = ChangePasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password changed. You can sign in now.', 'success')
        return redirect(url_for('users.login'))
    return render_template('main/change_password.html', title='Reset Password', form=form)
# request token actually, anyway doesn't work properly


@users.route('/user/<int:user_id>/password_change', methods=['GET', 'POST'])
@login_required
def password_change_manually(user_id):
    user = User.query.get_or_404(current_user.id)
    form = ChangePasswordManuallyForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your account info updated', 'success')
        return redirect(url_for('users.account'))
    return render_template('main/change_password_manually.html', title='Change Password', form=form, user=user)
