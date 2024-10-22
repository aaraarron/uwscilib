from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from app import db
from app.models import User, Book
from flask_login import login_required
from flask import request
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
@login_required
def index():
    form = EmptyForm()
    books= db.session.scalars(sa.select(Book)).all()
    return render_template('index.html', title='Home', books=books, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data.lower()))
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
    flash('successfully Iogged out')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.lower(), email=form.email.data, program=form.program.data, about_me='')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    form = EmptyForm()
    user = db.first_or_404(sa.select(User).where(User.username == username.lower()))
    checked_books = db.session.scalars(sa.select(Book).where(Book.checked_by == current_user))
    return render_template('user.html', user=user, checked_books=checked_books, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data.lower()
        current_user.program = form.program.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.program.data = current_user.program
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/checkout/<id>', methods=['GET', 'POST'])
@login_required
def checkout(id):
    form = EmptyForm()
    if form.validate_on_submit():
        book = db.session.scalar(
            sa.select(Book).where(Book.id == id))
        if book is None:
            flash(f'book {book.title} not found.')
            return redirect(url_for('index'))
        if book.checked_by == current_user:
            flash("You already checked out this book")
            return redirect(url_for('index'))
        current_user.check_book(book)
        db.session.commit()
        flash(f'You have checked out {book.title}!')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/returnbook/<id>', methods=['GET', 'POST'])
@login_required
def returnbook(id):
    form = EmptyForm()
    if form.validate_on_submit():
        book = db.session.scalar(
            sa.select(Book).where(Book.id == id))
        if book is None:
            flash(f'book {book.title} not found.')
            return redirect(url_for('index'))
        if not book.checked_by == current_user:
            flash("You cannot return a book you haven't checked out")
            return redirect(url_for('index'))
        u = db.session.scalar(sa.select(User).where(User.id == 1))
        book.checked_by = u
        db.session.commit()
        flash(f'You have returned {book.title}.')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/bookpage/<id>')
@login_required
def bookpage(id):
    form = EmptyForm()
    book = db.session.scalar(sa.select(Book).where(Book.id == id))
    return render_template('bookpage.html', book=book, form=form)
'''
import csv
@app.route('/update')
def update():
    u = db.session.scalar(sa.select(User).where(User.id == 1))
                    
    with open('books.csv', 'r') as file:
        reader = csv.reader(file)
        for book in reader:
            book = Book(book_isbn13=book[0], title=book[1], book_author=book[2], book_style=book[3], checked_by=u)
            db.session.add(book)
            db.session.commit()
    flash('done')
    return redirect(url_for('index'))'''
