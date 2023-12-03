from flask import Blueprint

from flask import render_template, url_for, flash, redirect, request, abort
from .forms import PostForm
#  UpdatePostForm?
from .. import db, bcrypt, mail
from ..models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = Blueprint('posts', __name__)




@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post1 = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post1)
        db.session.commit()
        flash('Post has been created', 'success')
        return redirect(url_for('main.home'))
    return render_template('main/post_create.html', title='New post', form=form)


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('main/post.html', title=post.title, post=post)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.id != Post.query.get_or_404(post_id).author.id:
        flash("It's not your post", 'danger')
        return redirect(url_for('posts.post', post_id=post_id))
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post info updated', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('main/updatepost.html', title=f'Update Post - {post.title}', post=post, form=form, legend=f'Update Post - {post.title}')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.id != Post.query.get_or_404(post_id).author.id:
        flash("It's not your post", 'danger')
        return redirect(url_for('posts.post', post_id=post_id))
    form = PostForm()
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted', 'success')
    return redirect(url_for('main.home'))
