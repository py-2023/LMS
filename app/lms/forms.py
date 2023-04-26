from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, EmailField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.auth.models import User, ReturnStatus


class AddBookForm(FlaskForm):

    title = StringField("Book Title", validators=[DataRequired()])
    authors = StringField("Authors", validators=[DataRequired()])
    publisher = StringField("Publisher", validators=[DataRequired()])
    edition = StringField("Edition", validators=[DataRequired()])
    isbn = StringField("ISBN", validators=[DataRequired()])
    shelfnum = StringField("Shelf Num", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    totalnoofcopies = IntegerField("Number of copies", validators=[DataRequired()])

    def validate(self, extra_validators=None):
        initial_validation = super(AddBookForm, self).validate()
        if not initial_validation:
            return False
        ## write other validations
        return True




class IssueBookForm(FlaskForm):

    book = StringField("Book Title", validators=[DataRequired()])
    #issued_to = StringField("Issued To", validators=[DataRequired()])
    issued_to = SelectField("Issued To")
    issued_date = StringField("Issuance Date", validators=[DataRequired()])
    to_be_returned_by_date = StringField("To be Returned by", validators=[DataRequired()])
    actual_return_date = StringField("Actual Return Date")
    returnstatus = SelectField("Return Status", choices=[(choice.name, choice.value) for choice in ReturnStatus])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = User.query.filter_by().all()

        self.issued_to.choices = [
            (user, user) for user in users
        ]



    def validate(self, extra_validators=None):
        initial_validation = super(IssueBookForm, self).validate()
        if not initial_validation:
            return False
        ## write other validations
        return True



class SearchBookForm(FlaskForm):
    title = StringField("Book Title")
    authors = StringField("Authors")
    isbn = StringField("ISBN")

    def validate(self, extra_validators=None):
        initial_validation = super(SearchBookForm, self).validate()
        if not initial_validation:
            return False
        ## write other validations
        return True




class RenewBookForm(FlaskForm):
    book = StringField("Book Title", validators=[DataRequired()])
    issued_to = StringField("Issued To", validators=[DataRequired()])
    issued_date = StringField("Issuance Date", validators=[DataRequired()])
    to_be_returned_by_date = StringField("To be Returned by", validators=[DataRequired()])
    actual_return_date = StringField("Actual Return Date")
    returnstatus = SelectField("Return Status", choices=[(choice.name, choice.value) for choice in ReturnStatus])


    def validate(self, extra_validators=None):
        initial_validation = super(RenewBookForm, self).validate()
        if not initial_validation:
            return False
        ## write other validations
        return True