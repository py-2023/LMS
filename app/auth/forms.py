from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.auth.models import User


class LoginForm(FlaskForm):
    userid = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    mobile = StringField("Mobile", validators=[DataRequired()])
    # is_admin = BooleanField('is Admin ?')
    # is_active = BooleanField('is Active ?', validators=[DataRequired()])

    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    def validate(self, extra_validators=None):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.email.errors.append(
                "Try a different username, User name already registered for user : " + str(user.username))
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append(
                "Try a different email, Email  already registered  for user: " + str(user.username))
            return False
        user = User.query.filter_by(mobile=self.mobile.data).first()
        if user:
            self.email.errors.append(
                "Try a different Mobile Number, Mobile number already registered for  user : " + str(user.username))
            return False

        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        ## write other validations
        return True


class UpdateForm(FlaskForm):
    userid = IntegerField("User Id")
    username = StringField("User Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    mobile = StringField("Mobile", validators=[DataRequired()])
    # is_admin = BooleanField('is Admin ?')
    # is_active = BooleanField('is Active ?', validators=[DataRequired()])

    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    def validate(self, extra_validators=None):
        initial_validation = super(UpdateForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter(User.username == self.username.data, User.userid != self.userid.data).first()
        if user:
            self.email.errors.append(
                "Try a different username, User name already registered for user : " + str(user.username))
            return False
        #user = User.query.filter_by(email=self.email.data).first()
        user = User.query.filter(User.email == self.email.data, User.userid != self.userid.data).first()
        if user:
            self.email.errors.append(
                "Try a different email, Email  already registered  for user: " + str(user.username))
            return False
        #user = User.query.filter_by(mobile=self.mobile.data).first()
        user = User.query.filter(User.mobile == self.mobile.data, User.userid != self.userid.data).first()
        if user:
            self.email.errors.append(
                "Try a different Mobile Number, Mobile number already registered for  user : " + str(user.username))
            return False

        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False

        return True

    # def __init__(self, *args, **kwargs):
    #    super(UpdateForm, self).__init__(*args, **kwargs)
    #    read_only(self.userid)
