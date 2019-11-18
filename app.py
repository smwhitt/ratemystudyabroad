from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import request
import models
import forms
from forms import WriteReview
from models import *

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})

@app.route('/all')
def all_drinkers():
    drinkers = db.session.query(models.Drinker).all()
    return render_template('all-drinkers.html', drinkers=drinkers)

@app.route('/review', methods=['GET', 'POST'])
def review():
    form = WriteReview()
    if form.validate_on_submit():
        return "location: {}, program: {}".format(form.location.data, form.program.data)
    return render_template('trying-shit-out.html', form = form)

# @app.route('/confused', methods=['GET', 'POST'])
# def confused():
#     form = WriteReview()
#     if form.validate_on_submit():
#         # review = Review()
#         # form.populate_obj(review)
#         # db.session.add(review)
#         # db.session.commit()
#         # location = form.location.data
#         # program = form.program.data
#         # course = form.course.data
#         # rating = form.rating.data
#         # difficulty = form.difficulty.data
#         # thoughts = form.thoughts.data
#         # print(location)
#         # print(program)
#         # print(course)
#         # print(rating)
#         # print(difficulty)
#         # print(thoughts)
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))
#         return redirect('/index')
#         # print("\nData received. Now redirecting ...")
#         # return redirect(url_for('confused'))
#     return render_template('trying-shit-out.html', form=form)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/homepage', methods=['GET', 'POST'])
def home_page():
    return render_template('home.html')

# ----------- EXAMPLE -------------
@app.route('/login-example', methods=["GET", "POST"])
def login_example():
    form = forms.EmailPasswordForm()
    if form.validate_on_submit():
        # return "email: {}, password: {}".format(form.email.data, form.password.data)
        return render_template('submitted.html',
            email=form.email.data, password=form.password.data)
    return render_template('login-example.html', form=form)

# ---------------------------------

@app.route('/filter')
def filter_reviews():
    courses = db.session.query(models.Course).all()
    return render_template('filter.html')
    # note, temporary render explore. change to render filter.html


@app.route('/write-review', methods=['GET'])
def write_review():
    courses = db.session.query(models.Course).all()
    programs = db.session.query(models.Program).all()
    countries = db.session.query(models.Program.country).distinct().all()
    return render_template('write-review.html', courses=courses, programs=programs, countries=countries)


@app.route('/submitted')
def submit_review():
    return render_template('submitted.html')


@app.route('/explore', methods=['GET'])
def explore_courses():
    courses = db.session.query(models.Course).all()
    programs = db.session.query(models.Program).all()
    return render_template('explore.html', courses=courses, programs=programs)

@app.route('/course-review/<course_name>')
def course_review(course_name):
    course = db.session.query(models.Course)\
        .filter(models.Course.course_name == course_name).one()
    reviews = db.session.query(models.Review)\
        .filter(models.Review.course_name == course_name)
    return render_template('course-review.html', course=course, reviews=reviews)
# fix filtering - use keys (multiple variables)

@app.route('/drinker/<name>')
def drinker(name):
    drinker = db.session.query(models.Drinker) \
        .filter(models.Drinker.name == name).one()
    return render_template('drinker.html', drinker=drinker)


@app.route('/edit-drinker/<name>', methods=['GET', 'POST'])
def edit_drinker(name):
    drinker = db.session.query(models.Drinker).filter(models.Drinker.name == name).one()
    beers = db.session.query(models.Beer).all()
    bars = db.session.query(models.Bar).all()
    form = forms.DrinkerEditFormFactory.form(drinker, beers, bars)
    if form.validate_on_submit():
        try:
            form.errors.pop('database', None)
            models.Drinker.edit(name, form.name.data, form.address.data,
                                form.get_beers_liked(), form.get_bars_frequented())
            return redirect(url_for('drinker', name=form.name.data))
        except BaseException as e:
            form.errors['database'] = str(e)
            return render_template('edit-drinker.html', drinker=drinker, form=form)
    else:
        return render_template('edit-drinker.html', drinker=drinker, form=form)


@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return singular if number in (0, 1) else plural


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
