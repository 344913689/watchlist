#coding:utf-8

import click
from watchlist import app, db
from watchlist.models import User, Movie


@app.cli.command()
@click.option('--drop', is_flag = True, help='create  after drop')
def initdb(drop):
    '''初始化数据库'''
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库成功')


@app.cli.command()
def forge():
    '''初始化数据'''
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