import os
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, CreatePostForm, AddWalletForm
from app.models import User, Post, Wallet
from urllib.parse import urlsplit


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    posts = db.session.scalars(user.posts.select()).all()
    # wallet = db.session.scalars(user.wallet.select()).all()
    wallet = None
    if user.wallet:
        wallet = user.wallet

    return render_template('index.html', title='Home',
                           posts=posts, wallet=wallet
                           )



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.body.data,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()
        flash('Congratulations')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='Create Post', form=form)


@app.route('/add-wallet', methods=['GET', 'POST'])
@login_required
def add_wallet():
    form = AddWalletForm()
    if form.validate_on_submit():
        post = Wallet(
            user_id=current_user.id,
            address=form.address.data,
            encrypted_private_key=form.encrypted_private_key.data,
            chain=form.chain.data

        )

        db.session.add(post)
        db.session.commit()
        flash('Congratulations')
        return redirect(url_for('index'))
    return render_template('add_wallet.html', title='Add Wallet', form=form)