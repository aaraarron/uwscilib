from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    program: so.Mapped[str] = so.mapped_column(sa.String(140), index=True)
    checked_books: so.WriteOnlyMapped['Book'] = so.relationship(back_populates='checked_by')

    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def check_book(self, book):
        if not self.is_checked(book):
            self.checked_books.add(book)

    def return_book(self, book):
        if self.is_checked(book):
            self.checked_books.remove(book)

    def is_checked(self, book):
        query = self.checked_books.select().where(Book.id == book.id)
        return db.session.scalar(query) is not None

    def checked_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.checked_books.select().subquery())
        return db.session.scalar(query)

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Book(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    book_author: so.Mapped[str] = so.mapped_column(sa.String(140))
    book_isbn13: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    book_style: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp_checked: so.Mapped[Optional[datetime]] = so.mapped_column(index=True, default=None)    
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    checked_by: so.Mapped[User] = so.relationship(back_populates='checked_books')

    def __repr__(self):
        return '<Book {}>'.format(self.title)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

