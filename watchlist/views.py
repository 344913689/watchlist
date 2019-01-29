#coding: utf-8

from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie

@app.route('/video')
def video():
    return '<video src="/static/temp.mkv"></video>'


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