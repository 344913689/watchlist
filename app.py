#coding:utf-8

import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
from flask import render_template, url_for, redirect, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/watch'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'dev'


login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)
        # 验证密码，返回布尔值


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.cli.command()
@click.option('--drop', is_flag = True, help='create  after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库成功')


@app.cli.command()
def forge():
    db.create_all()

    movies = [
        {'title': '龙猫', 'year': '1988'},
        {'title': '死亡诗社', 'year': '1989'},
        {'title': '完美的世界', 'year': '1993'},
        {'title': '这个杀手不太冷', 'year': '1994'},
        {'title': '麻将', 'year': '1996'},
        {'title': '燕尾蝶', 'year': '1996'},
        {'title': '喜剧之王', 'year': '1999'},
        {'title': '鬼子来了', 'year': '1999'},
        {'title': '机器人总动员', 'year': '2008'},
        {'title': '天下无贼', 'year': '2004'},
        {'title': '沉默爆裂', 'year': '2018'},
    ]

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    
    db.session.commit()
    click.echo('Done.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('更新用户...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('创建用户...')
        user = User(username = username, name = 'admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user = user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if notcurrent_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入错误，请重新输入！')
            return redirect(url_for('index'))
        movies = Movie(title=title, year=year)
        db.session.add(movies)
        db.session.commit()
        flash('添加成功！')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies = movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required #未登录用户不可见
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    print(request.method)
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(title) > 60 or len(year) > 4:
            flash('输入错误，请重新输入！')
            return redirect(url_for('edit', movie_id = movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('更新成功！')
        return redirect(url_for('index'))

    return render_template('edit.html', movie = movie)

@app.route('/movie/delete/<int:movie_id>', methods=['GET', 'POST'])
@login_required #未登录用户不可见
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('删除完成！')
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入错误！')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.name and user.validate_password(password):
            login_user(user)
            flash('登录成功！')
            return redirect(url_for('index'))

        flash('用户名或密码错误！')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required #用户视图保护
def logout():
    logout_user()
    flash('再见！')
    return redirect(url_for('index'))

