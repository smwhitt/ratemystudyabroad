import functools
import models
from models import *
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
bp = Blueprint('auth', __name__, url_prefix='/auth')
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        elif db.engine.execute(
            'SELECT email FROM models.Users WHERE username = username').fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.engine.execute(
                'INSERT INTO models.Users (username, password) VALUES (username, generate_password_hash(password))'
            )
            db.engine.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        uname = request.form['username']
        password = request.form['password']
        error = None
        user = db.session.query(models.Users).filter(models.Users.username == uname)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session.user_email = user.email
            return redirect(url_for('home_page'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_email = session.get('user_email')

    if user_email is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM Users WHERE email = ?', (user_email,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view