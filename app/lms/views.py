from datetime import datetime, timedelta

from flask import Blueprint, render_template
from flask_login import login_required

from sqlalchemy.exc import OperationalError
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import bcrypt, db
from app.auth.forms import LoginForm, RegisterForm
from app.auth.models import User, Book, BookIssuanceTracker
from app import login_manager  # the variable from Flask-login
from app.lms.forms import AddBookForm, IssueBookForm

lms_bp = Blueprint("lms", __name__)


## fixing issue with key -- userid instead of id
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@lms_bp.route("/addbook", methods=["GET", "POST"])
@login_required
def addbook():
    form = AddBookForm(request.form)
    if form.validate_on_submit():
        totalnoofcopies = form.totalnoofcopies.data
        book = Book(title=form.title.data, authors=form.authors.data, publisher=form.publisher.data,
                    edition=form.edition.data,shelfnum=form.shelfnum.data,
                    isbn=form.isbn.data, description=form.description.data, totalnoofcopies=form.totalnoofcopies.data,
                    availablenoofcopies=form.totalnoofcopies.data)

        try:

            for _ in range(totalnoofcopies):
                booksforissuance = BookIssuanceTracker()
                book.issuance.append(booksforissuance)
                db.session.add(book)
            db.session.commit()


        except:
            flash("Unable to commit", "success")

        print(form.errors)
        print(form)

        flash("Book entry added", "success")

        return render_template("lms/addbook.html", form=form)

    return render_template("lms/addbook.html", form=form)


@lms_bp.route("/issuebook", methods=["GET", "POST"])
@login_required
def issuebook():

    if request.method == 'GET':
        form = IssueBookForm(request.form)
        # list the books
        books = Book.query.filter(Book.availablenoofcopies > 0).all()
        if books:
            return render_template("lms/issuebook.html", books=Book.query.all(), form=form)
        flash("Books Available  for issue: 0")
        return render_template(
            "lms/issuebook.html", books=Book.query.all(), form=form)

    if request.method == 'POST':
        # issue book
        form = IssueBookForm(request.form)



        book_id = int(request.form.get("book"))

        bookissuance = BookIssuanceTracker.query.filter_by(book=book_id, issued_to=None).first()

        bookissuance.issued_to = current_user.userid
        bookissuance.bookissuance.availablenoofcopies -= 1  ## using backreference
        bookissuance.issuance_date = datetime.now()
        bookissuance.to_be_returned_by_date = datetime.now() + timedelta(days=7)
        db.session.commit()
        flash("Book issued !")
        return render_template(
            "lms/issuebook.html", books=Book.query.all(), form=form)


@lms_bp.route("/returnbook", methods=["GET", "POST"])
@login_required
def returnbook():
    if request.method == 'GET':
        form = IssueBookForm(request.form)
        # list the books
        booksissued = BookIssuanceTracker.query.filter_by(issued_to=current_user.userid).all()
        if booksissued:
            return render_template("lms/returnbook.html", booksissued=booksissued, form=form)
        flash("No Return Pending")
        return render_template(
            "lms/returnbook.html", booksissued=BookIssuanceTracker.query.all(), form=form)

    if request.method == 'POST':
        # issue book
        form = IssueBookForm(request.form)

        book_id = int(request.form.get("book"))

        bookissuance = BookIssuanceTracker.query.filter_by(book=book_id, issued_to=current_user.userid).first()

        bookissuance.issued_to = None
        bookissuance.bookissuance.availablenoofcopies += 1  ## using backreference
        bookissuance.issuance_date = None
        bookissuance.to_be_returned_by_date = None
        bookissuance.actual_return_date=datetime.now()
        db.session.commit()
        flash("Book Returned !")
        return render_template(
            "lms/returnbook.html", books=BookIssuanceTracker.query.all(), form=form)

