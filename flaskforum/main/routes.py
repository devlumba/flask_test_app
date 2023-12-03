from flask import Blueprint

from flask import render_template, url_for, flash, redirect, request, abort
from ..models import User, Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=10, page=page)
    return render_template('main/home.html', posts=posts)


@main.route("/about/")
def about():
    return render_template('main/about.html', title='About')

