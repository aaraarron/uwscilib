import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post, Book


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email='susan@uwaterloo.ca', program='math')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@uwaterloo.ca', program='chem')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/193d7e28d44e9b578ccccbd47a88af95?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@uwaterloo.ca', program='chem')
        u2 = User(username='library', email='library@uwaterloo.ca', program='library')
        b2 = Book(title='calculus', book_author='james stewart', book_style='binder', checked_by=u2)
        db.session.add(u1)
        db.session.add(b2)
        db.session.commit()
        Checked = db.session.scalars(u1.checked_books.select()).all()
        self.assertEqual(Checked, [])

        u1.check_book(b2)
        db.session.commit()
        self.assertTrue(u1.is_checked(b2))
        self.assertEqual(u1.checked_count(), 1)
        u1_checked = db.session.scalars(u1.checked_books.select()).all()
        b2_checked_by = db.session.scalars(b2.checked_by).all()
        self.assertEqual(u1_checked[0].title, 'calculus')
        self.assertEqual(b2_checked_by[0].username, 'library')

        u1.return_book(b2)
        db.session.commit()
        self.assertFalse(u1.is_checked(b2))
        self.assertEqual(u1.checked_count(), 0)

 
if __name__ == '__main__':
    unittest.main(verbosity=2)
