from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    subject = SelectField('Subject', choices=[
        ('Data science', 'Data science'),
        ('Maths', 'Maths'),
        ('Electronics', 'Electronics'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
        ('Block Chain', 'Block Chain')
    ])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('User Type', choices=[('student', 'Student'), ('instructor', 'Instructor')])
    subject = SelectField('Subject', choices=[
        ('Data science', 'Data science'),
        ('Maths', 'Maths'),
        ('Electronics', 'Electronics'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
        ('Block Chain', 'Block Chain')
    ])
    year_of_study = IntegerField('Year of Study')
    interested_courses = StringField('Interested Courses')
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    video_resources = TextAreaField('Video Resources (One link per line)')
    pdf_resources = TextAreaField('PDF Resources (One link per line)')
    assignment_link = StringField('Assignment Link')
    submit = SubmitField('Submit')

class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired()])
    description = TextAreaField('Assignment Description', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    course = SelectField('Course', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Assignment')