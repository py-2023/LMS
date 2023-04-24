from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.auth.models import User


class LoginForm(FlaskForm):
    userid = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    mobile = StringField("Mobile", validators=[DataRequired()])
    is_admin = BooleanField('is Admin ?')
    is_active = BooleanField('is Active ?', validators=[DataRequired()])

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
        user = User.query.filter_by(userid=self.username.data).first()
        if user:
            self.email.errors.append("User name already registered")
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        ## write other validations
        return True
