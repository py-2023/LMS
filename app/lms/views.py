from datetime import datetime, timedelta

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import or_, and_

from sqlalchemy.exc import OperationalError
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import bcrypt, db
from app.auth.forms import LoginForm, RegisterForm, UpdateForm
from app.auth.models import User, Book, BookIssuanceTracker, BookIssuanceHistory
from app import login_manager  # the variable from Flask-login
from app.lms.forms import AddBookForm, IssueBookForm, RenewBookForm, SearchBookForm

lms_bp = Blueprint("lms", __name__)


## fixing issue with key -- userid instead of id
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))






@lms_bp.route("/addbook", methods=["GET", "POST"])
@login_required
def addbook():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))




    if request.method == 'GET':
        form = AddBookForm(request.form)

        return render_template("lms/addbook.html", form=form)

    if request.method == 'POST':

        form = AddBookForm(request.form)
        if form.validate:
            totalnoofcopies = form.totalnoofcopies.data
            book = Book(title=form.title.data, authors=form.authors.data, publisher=form.publisher.data,
                        edition=form.edition.data, shelfnum=form.shelfnum.data,
                        isbn=form.isbn.data, description=form.description.data,
                        totalnoofcopies=form.totalnoofcopies.data,
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
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))

    if request.method == 'GET':
        form = IssueBookForm(request.form)
        # list the books
        books = Book.query.filter(Book.availablenoofcopies > 0).all()
        ## To remove librarian from the person to whom book is to be issued
        ## user with isadmin=True is librarian
        # users = User.query.filter_by(is_admin=False).all()
        users = User.query.filter(and_(User.is_admin == False, User.is_active == True)).all()

        if books:
            return render_template("lms/issuebook.html", books=Book.query.all(), users=users, form=form)
        flash("Books Available  for issue: 0")
        users = User.query.filter(and_(User.is_admin == False, User.is_active == True)).all()
        return render_template(
            "lms/issuebook.html", books=Book.query.all(), users=users, form=form)

    if request.method == 'POST':
        # issue book
        form = IssueBookForm(request.form)

        book_id = int(request.form.get("book"))
        issued_to = request.form.get("issued_to")
        issued_to_user = User.query.filter_by(userid=issued_to).first()

        bookissuance = BookIssuanceTracker.query.filter_by(book=book_id, issued_to=None).first()
        book = Book.query.filter_by(id=book_id).first()
        bookissuance.issued_to = issued_to
        bookissuance.bookissuance.availablenoofcopies -= 1  ## using backreference
        print("#############Available copy -1 ")
        bookissuance.issuance_date = datetime.now()
        bookissuance.to_be_returned_by_date = datetime.now() + timedelta(days=7)
        db.session.add(bookissuance)
        db.session.commit()

        bookIssuanceHistory = BookIssuanceHistory(book=book_id,
                                                  title=book.title,
                                                  authors=book.authors,
                                                  publisher=book.publisher,
                                                  edition=book.edition,
                                                  isbn=book.isbn,
                                                  userid=issued_to_user.userid,
                                                  username=issued_to_user.username,
                                                  issuance_date=bookissuance.issuance_date,
                                                  actual_return_date=None,
                                                  returnstatus="PENDING_RETURN"
                                                  )

        try:

            db.session.add(bookIssuanceHistory)
            db.session.commit()


        except:
            flash("Unable to commit", "success")

        flash("Book issued ")
        users = User.query.filter(and_(User.is_admin == False, User.is_active == True)).all()
        return render_template(
            "lms/issuebook.html", books=Book.query.all(), users=users, form=form)


@lms_bp.route("/returnbook", methods=["GET", "POST"])
@login_required
def returnbook():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))
    if request.method == 'GET':
        form = IssueBookForm(request.form)
        # list the books

        booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all()

        if booksissued:
            return render_template("lms/returnbook.html", booksissued=booksissued, form=form)
        flash("No Return Pending")
        return render_template(
            "lms/returnbook.html", booksissued=booksissued,
            form=form)

    if request.method == 'POST':
        # issue book
        form = IssueBookForm(request.form)
        datetimenow = datetime.now()

        book_id = int(request.form.get("book"))
        issued_to = request.form.get("issued_to")
        issued_to_user = User.query.filter_by(userid=issued_to).all()

        bookissuance = BookIssuanceTracker.query.filter(BookIssuanceTracker.book==book_id,BookIssuanceTracker.issued_to==issued_to).first()

        bookissuedto = bookissuance.issued_to
        issuance_date = bookissuance.issuance_date

        bookissuance.issued_to = None
        bookissuance.bookissuance.availablenoofcopies += 1  ## using backreference
        bookissuance.issuance_date = None
        bookissuance.to_be_returned_by_date = None
        bookissuance.actual_return_date = None
        bookissuance.returnstatus = None
        db.session.add(bookissuance)
        db.session.commit()
        flash("Book Returned ")

        try:
            # using issuance date as part of filter to identify the record
            bookissuance = BookIssuanceHistory.query.filter_by(book=book_id, userid=bookissuedto,
                                                               issuance_date=issuance_date).first()

            bookissuance.actual_return_date = datetimenow
            bookissuance.returnstatus = "RETURNED"

            db.session.commit()


        except Exception as error:

            print(error)
            flash("Unable to commit" + str(error), "success")

        booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all()

        return render_template(
            "lms/returnbook.html",
            booksissued=booksissued,
            form=form)


@lms_bp.route("/renewbook", methods=["GET", "POST"])
@login_required
def renewbook():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))
    if request.method == 'GET':
        form = IssueBookForm(request.form)
        # list the books which are issued for renewal screen
        booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all()

        if booksissued:
            return render_template("lms/renewbook.html", booksissued=booksissued, form=form)
        flash("No Return Pending")
        return render_template(
            "lms/renewbook.html", booksissued=booksissued, form=form)

    if request.method == 'POST':
        # issue book
        form = RenewBookForm(request.form)

        book_id = int(request.form.get("book"))

        bookissuance = BookIssuanceTracker.query.filter_by(book=book_id).first()

        # bookissuance.bookissuance.availablenoofcopies += 1  ## using backreference
        bookissuedto = bookissuance.issued_to
        issuance_date = bookissuance.issuance_date
        newreturndate = datetime.now() + timedelta(days=7)

        # bookissuance.issuance_date = datetime.now()
        bookissuance.to_be_returned_by_date = newreturndate
        db.session.add(bookissuance)
        db.session.commit()

        flash("Book Re-Issued")
        booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all()

        try:
            # using issuance date as part of filter to identify the record
            bookissuance = BookIssuanceHistory.query.filter_by(book=book_id, userid=bookissuedto,
                                                               issuance_date=issuance_date).first()

            bookissuance.actual_return_date = None

            db.session.add(bookissuance)
            db.session.commit()


        except Exception as error:

            print(error)
            flash("Unable to commit" + str(error), "success")
            booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all()

        return render_template(
            "lms/renewbook.html", booksissued=booksissued,
            form=form)


@lms_bp.route("/issuedbooks", methods=["GET", "POST"])
@login_required
def issuedbook():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))
    if request.method == 'GET':
        booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all()
        # booksissued = BookIssuanceTracker.query.filter_by(issued_to=current_user.userid).all()
        if booksissued:
            return render_template("lms/issuedbooks.html", booksissued=booksissued)
        flash("No Books issued")
        return render_template(
            "lms/issuedbooks.html",
            booksissued=booksissued)

    if request.method == 'POST':
        # issue book

        return render_template(
            "lms/issuedbooks.html",
            booksissued=BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to != None).all())


@lms_bp.route("/searchbooks", methods=["GET", "POST"])
@login_required
def searchbook():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))
    if request.method == 'GET':
        form = SearchBookForm(request.form)
        # list the books
        books = Book.query.filter().all()
        if books:
            return render_template("lms/searchbook.html", searchresult=Book.query.filter().all(), form=form)
        flash("Books Available in system are listed. Use search option to search with book title")
        return render_template(
            "lms/searchbook.html", searchresult=Book.query.all(), form=form)

    if request.method == 'POST':
        # issue book
        form = SearchBookForm(request.form)

        title = str(request.form.get("title"))

        searchresult = Book.query.filter(
            or_(Book.title.contains(title), Book.authors.contains(title), Book.isbn.contains(title))).all()
        if searchresult:
            return render_template("lms/searchbook.html", searchresult=searchresult, form=form)
        flash("No Books matching name or authors or isbn")
        return render_template(
            "lms/searchbook.html", searchresult=searchresult, form=form)


@lms_bp.route("/listmembers", methods=["GET", "POST"])
@login_required
def listmembers():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))
    if request.method == 'GET':
        form = UpdateForm(request.form)
        users = User.query.filter_by().all()
        if users:
            return render_template("lms/memberlist.html", users=users, form=form)
        flash("user list")
        return render_template(
            "lms/memberlist.html",
            users=users)

    if request.method == 'POST':
        userid = int(request.form.get("book"))

        user = User.query.filter_by(userid=userid).first()
        form = UpdateForm(request.form)

        form.userid.data = user.userid
        form.username.data = user.username
        form.mobile.data = user.mobile
        form.email.data = user.email

        return render_template("authentication/updateuser.html", form=form)


@lms_bp.route("/bookhistory", methods=["GET", "POST"])
@login_required
def bookhistory():
    if not current_user.is_admin:
        flash("Access restricted to librarian", "success")
        return redirect(url_for("homepage.index"))
    if request.method == 'GET':
        bookrecords = BookIssuanceHistory.query.filter_by().all()
        if bookrecords:
            return render_template("lms/bookhistory.html", bookrecords=bookrecords)
        flash("No Records Available")
        return render_template(
            "lms/bookhistory.html",
            bookrecords=bookrecords)


@lms_bp.route("/myissuedbookslist", methods=["GET", "POST"])
@login_required
def myissuedbookslist():
    if request.method == 'GET':
        booksissued = BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to == current_user.userid).all()
        # booksissued = BookIssuanceTracker.query.filter_by(issued_to=current_user.userid).all()
        if booksissued:
            return render_template("lms/issuedbooks.html", booksissued=booksissued)
        flash("No Books issued")
        return render_template(
            "lms/issuedbooks.html",
            booksissued=booksissued)

    if request.method == 'POST':
        # issue book

        return render_template(
            "lms/issuedbooks.html",
            booksissued=BookIssuanceTracker.query.filter(BookIssuanceTracker.issued_to == current_user.userid).all())


@lms_bp.route("/myissuedbookshistory", methods=["GET", "POST"])
@login_required
def myissuedbookshistory():
    if request.method == 'GET':
        bookrecords = BookIssuanceHistory.query.filter_by(userid=current_user.userid).all()
        if bookrecords:
            return render_template("lms/bookhistory.html", bookrecords=bookrecords)
        flash("No Records Available")
        return render_template(
            "lms/bookhistory.html",
            bookrecords=bookrecords)


@lms_bp.route("/updatemydetails", methods=["GET", "POST"])
@login_required
def updatemydetails():
    if request.method == 'GET':
        user = User.query.filter_by(userid=current_user.userid).first()
        form = UpdateForm(request.form)

        form.userid.data = user.userid
        form.username.data = user.username
        form.mobile.data = user.mobile
        form.email.data = user.email

        return render_template("authentication/updatemydetails.html", form=form)


    if request.method == 'POST':
        form = UpdateForm(request.form)

        if form.validate():
            user = User.query.filter_by(userid=form.userid.data).first()
            user.email = form.email.data
            user.username = form.username.data
            user.mobile = form.mobile.data
            user.password = bcrypt.generate_password_hash(form.password.data )

            try:
                db.session.add(user)
                db.session.commit()
                # login_user(user)
                flash("The user updation is complete for member id  :  " + str(user.userid) + "    ", "success")
            except:
                flash("Unable to update", "success")

            return redirect(url_for("homepage.index"))
        print(" validation failed")
        print(form.errors)
        print(form)

        return render_template("authentication/updateuser.html", form=form)






