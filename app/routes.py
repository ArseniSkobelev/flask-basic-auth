import datetime

import jwt

from flask_db import app, db
from flask import (Flask, render_template, redirect, url_for, request, make_response)
from app import models
from werkzeug.security import generate_password_hash, check_password_hash

import forms


@app.route('/')
def index():
    users = models.User.query.all()
    token = request.cookies.get('token')
    return render_template('index.html', users=users, token=token)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', '', expires=0)
    response.set_cookie('id', '', expires=0)
    return response


@app.route('/user')
def user():
    if request.cookies.get('token') is not None:
        print(request.cookies.get('token'))
        user_id = request.cookies.get('id')
        token = request.cookies.get('token')

        u = models.User.query.filter_by(id=user_id).first()

        return render_template('user.html', user=u, token=token)
    else:
        return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = forms.SignUpForm()

    if form.validate_on_submit():
        try:
            u = models.User(username=form.username.data.lower(), email=form.email.data,
                            password_hash=generate_password_hash(form.password.data))
            db.session.add(u)
            db.session.commit()
            print('signed up')
            return redirect(url_for('index'))
        except:
            print('err')

    return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    token = request.cookies.get('token')

    if form.validate_on_submit():
        u = models.User.query.filter_by(username=form.username.data.lower()).first()
        if u is not None:
            hashed = u.password_hash
            print("user exists, data retrieved successfully")
            if hashed is not None:
                if check_password_hash(hashed, form.password.data):
                    token = jwt.encode({'id': u.id,
                                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)},
                                       app.config['SECRET_KEY'], "HS256")
                    response = make_response(render_template('user.html', user=u, token=token))
                    response.set_cookie('token', token)
                    response.set_cookie('id', str(u.id))
                    return response
                else:
                    return redirect(url_for('login'))
        else:
            print("err; user not found")
            return redirect(url_for('login', stat='403'))
    return render_template('login.html', form=form, token=token)
