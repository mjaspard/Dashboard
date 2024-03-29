from webapp import app 
from flask import render_template, flash , redirect, url_for, request
from webapp.forms import LoginForm, RegistrationForm, AddServerForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from webapp.models import User, Server, Post
from werkzeug.urls import url_parse
from webapp import db
from datetime import datetime
import subprocess
import re
import os
from webapp.email import send_password_reset_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.username, device=form.device.data)
        db.session.add(post)
        db.session.commit()
        flash('Your comment is recorded')
        return redirect(url_for('index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Home', posts=posts, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
        return redirect(next_page )
    return render_template('login.html', title='Sign in', form=form)

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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
        user = User.query.filter_by(username=username).first_or_404()
        posts = Post.query.order_by(Post.timestamp.desc()).filter_by(user_id=username)
        return render_template('user.html', user=user, posts=posts)

@app.route('/AddServer', methods=['GET', 'POST'])
@login_required
def AddServer():
    form = AddServerForm(1)
    if form.validate_on_submit():
        server = Server(address=form.address.data, name=form.name.data, public_server=form.public_server.data, public_address=form.public_address.data, public_name=form.public_name.data, user=form.user.data, about_me=form.about_me.data)
        # server.get_sysinfo()
        # server.get_modele()
        # server.get_raminfo()
        # server.get_os()
        # server.get_cpuinfo()
        db.session.add(server)
        db.session.commit()
        flash('Thanks for adding this server!')
        return redirect(url_for('dashboard'))
    return render_template('edit_Server.html', title='Dashboard', form=form)


@app.route('/edit_server/<name>', methods=['GET', 'POST'])
@login_required
def edit_server(name):
    form = AddServerForm(0)
    server_current = Server.query.filter_by(name=name).first()
    print(server_current)
    if form.validate_on_submit():
        server_update = Server.query.filter_by(name=name).first()
        server_update.address = form.address.data
        server_update.name = form.name.data
        server_update.public_address=form.public_address.data
        server_update.public_name = form.public_name.data
        server_update.public_server = form.public_server.data
        server_update.user = form.user.data
        server_update.about_me = form.about_me.data
        server_update.ssh_connection = form.ssh_connection.data
        db.session.commit()
        flash('Thanks for modifying this server!')
        return redirect(url_for('server', server=server_update.name))
    elif request.method == 'GET':
        form.address.data = server_current.address
        form.name.data = server_current.name
        if server_current.public_address != None:
            form.public_address.data = server_current.public_address 
        else:
            form.public_address.data = '0.0.0.0'
        if server_current.public_name != None:
            form.public_name.data = server_current.public_name
        else:
            form.public_name.data = 'hostname'
        form.public_server.data = server_current.public_server
        form.about_me.data = server_current.about_me
        form.user.data = server_current.user
        form.ssh_connection.data = server_current.ssh_connection
    return render_template('edit_server.html', title='Dashboard', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    servers = Server.query.all()
    return render_template('dashboard.html', title='Dashboard', data=servers)

@app.route('/toggle_ssh/<server>', methods=['GET', 'POST'])
@login_required
def toggle_ssh(server):
    server = Server.query.filter_by(name=server).first()
    server.ssh_connection = server.toggle_ssh()
    db.session.commit()
    servers = Server.query.all()
    return render_template('dashboard.html', title='Dashboard', data=servers)

@app.route('/monitoring', methods=['GET', 'POST'])
@login_required
def monitoring():
    servers = Server.query.all()
    return render_template('monitoring.html', title='Monitoring', data=servers)

@app.route('/update_all_server', methods=['GET', 'POST'])
@login_required
def update_all_server():
    servers = Server.query.all()
    for server in servers:
        server.get_modele()
        server.get_raminfo()
        server.get_os()
        server.get_cpuinfo()
        server.get_sysinfo()
        db.session.commit()
        msg = "Update done for server {}".format(server)
        flash(msg)
    return redirect(url_for('dashboard'))

@app.route('/update_server/<server>', methods=['GET', 'POST'])
@login_required
def update_server(server):
    server = Server.query.filter_by(name=server).first()
    if server.test_connect() != "OK":
        msg = "SSH access failed: Please copy ssh key to {} server".format(server)
    else:
        server.get_modele()
        server.get_raminfo()
        server.get_os()
        server.get_cpuinfo()
        server.get_sysinfo()
        db.session.commit()
        msg = "Update done for server {}".format(server)
    flash(msg)
    return redirect(url_for('server', server=server.name))

@app.route('/dashboard/<server>')
@login_required
def server(server):
        server_x = Server.query.filter_by(name=server).first_or_404()
        posts = Post.query.order_by(Post.timestamp.desc()).filter_by(device=server)
        return render_template('server.html', server=server_x, posts=posts, os=os)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/post_delete/<id>')
@login_required
def post_delete(id):
    post = Post.query.filter_by(id=id).first()
    if post:
        if post.user_id == current_user.username:
            msg_text = 'Post well deleted'
            db.session.delete(post)
            db.session.commit()
            flash(msg_text)
        else:
            msg_text = 'Not possible, you are not the owner of this comment'
            flash(msg_text)
    # return redirect(url_for('index'))
    return redirect(request.referrer)



@app.route('/server_delete/<id>')
@login_required
def server_delete(id):
    server = Server.query.filter_by(id=id).first()
    if server:
        if current_user.username == 'maxime':
            msg_text = 'Server well deleted'
            db.session.delete(server)
            db.session.commit()
            flash(msg_text)
        else:
            msg_text = 'Not possible, only superuser are allowed to delete'
            flash(msg_text)
    return redirect(url_for('index'))