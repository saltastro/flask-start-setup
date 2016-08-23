from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 64)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')
