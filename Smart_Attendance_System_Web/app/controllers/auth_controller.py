from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app.models.teacher import Teacher

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def home():
    """
    Render the home page with login form
    """
    if 'teacher_id' in session:
        return redirect(url_for('analytics.dashboard'))
    return render_template('home.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle teacher login
    """
    email = request.form.get('email')
    password = request.form.get('password')

    print(f"Login attempt - Email: {email}, Password: {password}")

    if not email or not password:
        print("Missing email or password")
        flash('Please provide both email and password', 'error')
        return redirect(url_for('auth.home'))

    # Verify teacher credentials
    print("Calling Teacher.verify_password...")
    verification_result = Teacher.verify_password(email, password)
    print(f"Password verification result: {verification_result}")

    if verification_result:
        print("Password verified, getting teacher details...")
        teacher = Teacher.get_by_email(email)
        if teacher:
            print(f"Teacher found: ID={teacher.t_id}, Name={teacher.name}")
            session['teacher_id'] = teacher.t_id
            session['teacher_name'] = teacher.name
            session['teacher_email'] = teacher.email
            print("Session created, redirecting to dashboard")
            return redirect(url_for('analytics.dashboard'))
        else:
            print("Teacher not found after password verification!")
    else:
        print("Password verification failed")

    flash('Invalid email or password', 'error')
    return redirect(url_for('auth.home'))

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """
    Handle teacher logout
    """
    session.clear()
    return redirect(url_for('auth.home'))
