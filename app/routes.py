from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Course, Enrollment, Resource, Assignment
from app.forms import LoginForm, RegistrationForm, CourseForm, AssignmentForm
from app.utils import generate_otp, send_otp_email

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
student = Blueprint('student', __name__)
instructor = Blueprint('instructor', __name__)

@main.route('/')
def index():
    return render_template('base.html')

# Auth routes

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            otp = generate_otp()
            send_otp_email(user.email, otp)
            return redirect(url_for('auth.verify_otp', user_id=user.id, otp=otp))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@auth.route('/verify_otp/<int:user_id>/<otp>', methods=['GET', 'POST'])
def verify_otp(user_id, otp):
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == otp:
            user = User.query.get(user_id)
            login_user(user)
            if user.user_type == 'student':
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('instructor.dashboard'))
        else:
            flash('Invalid OTP. Please try again.')
    return render_template('verify_otp.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, user_type=form.user_type.data,
                    subject=form.subject.data, year_of_study=form.year_of_study.data,
                    interested_courses=form.interested_courses.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# Instructor routes
@instructor.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'instructor':
        flash('Access denied. Instructor only area.')
        return redirect(url_for('main.index'))
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    return render_template('instructor_dashboard.html', courses=courses)
@instructor.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(name=form.name.data, subject=current_user.subject,
                        instructor_id=current_user.id, description=form.description.data,
                        assignment_link=form.assignment_link.data)
        db.session.add(course)
        db.session.commit()
        
        for video_link in form.video_resources.data.split(','):
            if video_link.strip():
                resource = Resource(course_id=course.id, type='video', link=video_link.strip())
                db.session.add(resource)
        
        for pdf_link in form.pdf_resources.data.split(','):
            if pdf_link.strip():
                resource = Resource(course_id=course.id, type='pdf', link=pdf_link.strip())
                db.session.add(resource)
        
        db.session.commit()
        flash('Course added successfully.')
        return redirect(url_for('instructor.dashboard'))
    return render_template('course_edit.html', form=form, title='Add Course')

@instructor.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('You do not have permission to edit this course.')
        return redirect(url_for('instructor.dashboard'))
    
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.name = form.name.data
        course.description = form.description.data
        course.assignment_link = form.assignment_link.data
        
        Resource.query.filter_by(course_id=course.id).delete()
        
        for video_link in form.video_resources.data.split(','):
            if video_link.strip():
                resource = Resource(course_id=course.id, type='video', link=video_link.strip())
                db.session.add(resource)
        
        for pdf_link in form.pdf_resources.data.split(','):
            if pdf_link.strip():
                resource = Resource(course_id=course.id, type='pdf', link=pdf_link.strip())
                db.session.add(resource)
        
        db.session.commit()
        flash('Course updated successfully.')
        return redirect(url_for('instructor.dashboard'))
    
    return render_template('course_edit.html', form=form, title='Edit Course')


@instructor.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    form = AssignmentForm()
    form.course.choices = [(c.id, c.name) for c in Course.query.filter_by(instructor_id=current_user.id).all()]
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            course_id=form.course.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment added successfully.')
        return redirect(url_for('instructor.dashboard'))
    return render_template('add_assignment.html', form=form)

# Student routes

@student.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'student':
        flash('Access denied. Student only area.')
        return redirect(url_for('main.index'))
    courses = Course.query.filter_by(subject=current_user.subject).all()
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('student_dashboard.html', courses=courses, enrollments=enrollments)


@student.route('/join_course/<int:course_id>')
@login_required
def join_course(course_id):
    course = Course.query.get_or_404(course_id)
    if Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first():
        flash('You are already enrolled in this course.')
    else:
        enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Congratulations! You have successfully joined the course.')
    
    # Redirect to the course view page instead of the dashboard
    return redirect(url_for('student.view_course', course_id=course_id))

@student.route('/view_course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    resources = Resource.query.filter_by(course_id=course_id).all()
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    is_enrolled = enrollment is not None

    return render_template('course_view.html', course=course, resources=resources, assignments=assignments, is_enrolled=is_enrolled)
    
    
@student.route('/complete_resource/<int:resource_id>')
@login_required
def complete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    resource.completed = True
    db.session.commit()
    flash('Resource marked as completed.')
    return redirect(url_for('student.view_course', course_id=resource.course_id))

@student.route('/browse_courses')
@login_required
def browse_courses():
    courses = Course.query.all()
    return render_template('browse_courses.html', courses=courses)

@student.route('/view_assignments')
@login_required
def view_assignments():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    course_ids = [enrollment.course_id for enrollment in enrollments]
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
    return render_template('view_assignments.html', assignments=assignments)

@student.route('/track_progress')
@login_required
def track_progress():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('track_progress.html', enrollments=enrollments)