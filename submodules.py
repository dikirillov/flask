from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Optional
import pdfkit


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ResumeForm(LoginForm):
    full_name = StringField('Full name', validators=[Optional()])
    birth_date = StringField('Birth date', validators=[Optional()])
    contact_email = StringField('Contact email', validators=[Optional()])
    contact_phone = StringField('Contact phone', validators=[Optional()])
    submit_create = SubmitField('Create!')
    submit_save = SubmitField('Save fields')

    def generate(self, name, date, email, phone):
        self.full_name.data = name
        self.birth_date.data = date
        self.contact_email.data = email
        self.contact_phone.data = phone


class User:
    def __init__(self):
        self.id = ""
        self.username = ""
        self.email = ""
        self.password_hash = ""
        self.full_name = ""
        self.birth_date = ""
        self.contact_email = ""
        self.contact_phone = ""

    def create_resume(self):
        with open("templates/resume.html", "w") as resume:
            html_str = f"""
            <body>
            <h1 style="text-align: center">Resume</h1>
            <div class="container">
            <h1 style="font-weight: normal">Full Name - {self.full_name}</h1>
            <h1 style="font-weight: normal">Birth date - {self.birth_date}</h1>
            <h1 style="font-weight: normal">Contact email - {self.contact_email}</h1>
            <h1 style="font-weight: normal">Contact phone - {self.contact_phone}</h1>
            </div>"""

            html_str += "</body>"

            resume.write(html_str)
        pdfkit.from_file("templates/resume.html", "resume.pdf")