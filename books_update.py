import csv
from app import app, db
from app.models import User, Post, Book
import sqlalchemy as sa
import sqlalchemy.orm as so

app.app_context().push()
u = User(username='library', email='library@uwaterloo.ca', program='library')
db.session.add(u)
                
with open('books.csv', 'r') as file:
    
    reader = csv.reader(file)
    for book in reader:
        book = Book(book_isbn13=book[0], title=book[1], book_author=book[2], book_style=book[3], checked_by=u)
        db.session.add(book)
        db.session.commit()





