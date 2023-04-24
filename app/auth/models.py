import enum
from datetime import datetime

from flask import current_app

from flask_login import UserMixin
from sqlalchemy import DateTime, func

from app import bcrypt, db


class ReturnStatus(enum.Enum):
    RETURNED = "Returned"
    YETTOBERETRUNED = "Yet to be Returned"


class User(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(200), unique=True)
    mobile = db.Column(db.String(15), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, unique=False, default=True)
    bookissuancebyuser = db.relationship("BookIssuanceTracker", backref="bookissuancebyuser", lazy=True)
    created_on = db.Column(db.DateTime, server_default=func.now())

    # Below code for https://stackoverflow.com/questions/37472870/login-user-fails-to-get-user-id
    def get_id(self):
        return self.userid

    def is_admin(self):
        return self.is_admin

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __init__(self, username, email, mobile, password, is_admin, is_active):
        self.is_active = is_active
        self.mobile = mobile

        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password)  # passwordhash is saved
        self.created_on = datetime.now()
        self.is_admin = is_admin


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    authors = db.Column(db.String(255))
    publisher = db.Column(db.String(255))
    edition = db.Column(db.String(255))
    isbn = db.Column(db.String(255))
    shelfnum = db.Column(db.Integer)
    description = db.Column(db.Text)
    issuance = db.relationship("BookIssuanceTracker", backref=db.backref("bookissuance", lazy=True), cascade="all")
    totalnoofcopies = db.Column(db.Integer)
    availablenoofcopies = db.Column(db.Integer)
    entry_created_on = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return '<Book {}>'.format(self.title)



    def __init__(self, title, authors, publisher, edition, shelfnum, isbn, description, totalnoofcopies,
                 availablenoofcopies):
        self.title = title
        self.authors = authors

        self.publisher = publisher
        self.edition = edition
        self.shelfnum = shelfnum
        self.isbn = isbn
        self.description = description
        self.totalnoofcopies = totalnoofcopies
        self.availablenoofcopies = availablenoofcopies


class BookIssuanceTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, db.ForeignKey("book.id"))
    issued_to = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=True, default=None)  ## with lib users
    issuance_date = db.Column(db.DateTime(), default=None)
    to_be_returned_by_date = db.Column(db.DateTime(), default=None)
    actual_return_date = db.Column(db.DateTime(), default=None)
    returnstatus = db.Column(db.Enum(ReturnStatus))
    entry_created_on = db.Column(db.DateTime, server_default=func.now())
    entry_updated_on = db.Column(db.DateTime, onupdate=func.now())
