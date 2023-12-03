import secrets
import os
from flask import render_template, url_for, flash, redirect, request, abort, current_app
from .. import mail
from ..models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from flask_mail import Message



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (240, 240)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreplynoreplynoreplynoreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset password, visit this link:
{url_for('users.change_password', token=token, _external=True)}

If you didn't request it, ignore this message
    '''
    mail.send(msg)

