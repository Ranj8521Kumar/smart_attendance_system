from flask import Flask, request, jsonify
import mysql.connector
import os
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, render_template_string
import mysql.connector
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from model.recognition import recognize_faces_in_image
import uuid
import threading
import time
import cv2
from attendance_update import update_attendance ,create_date_column_if_not_exists
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
from itsdangerous import URLSafeTimedSerializer



# Load environment variables from .env file
load_dotenv()

# Retrieve the values from the environment
SECRET_KEY = os.getenv('SECRET_KEY')
SECURITY_SALT = os.getenv('SECURITY_SALT')
server_url = os.getenv('SERVER_URL')

app = Flask(__name__)
CORS(app, resources={r"/get_attendance": {"origins": "*"}, r"/Attendance_Records/*": {"origins": "*"}})

# Set the secret key for Flask
app.config['SECRET_KEY'] = SECRET_KEY

# MySQL Connection using env variables
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Email validation with regex for better security
    if not re.match(r"[^@]+@rgipt.ac.in", email):
        return jsonify({'success': False, 'message': 'Email must end with @rgipt.ac.in and be in a valid format'}), 400

    # Database query and password check
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
        user = cursor.fetchone()
    finally:
        conn.close()  # Ensure connection is closed after the query

    if user and check_password_hash(user['password'], password):
        user.pop('password', None)  # Remove password from the response
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'teacher': user
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    # Ensure email is provided
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    # Validate email format
    if not re.match(r"[^@]+@rgipt.ac.in", email):
        return jsonify({'success': False, 'message': 'Email must end with @rgipt.ac.in and be in a valid format'}), 400

    # Check if email exists in the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
        user = cursor.fetchone()
    finally:
        conn.close()  # Ensure connection is closed after the query

    if user:
        try:
            send_reset_email(email)
            return jsonify({'success': True, 'message': f'Reset link sent to {email}'}), 200
        except Exception as e:
            print(f"Error sending email: {e}")
            return jsonify({'success': False, 'message': 'Failed to send email'}), 500
    else:
        return jsonify({'success': False, 'message': 'Email not found'}), 404
    
    


SENDER_EMAIL = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASS')

def send_reset_email(to_email):
    subject = "Reset Your Smart Attendance Password"
    
    # 🔐 Generate secure token and reset link
    token = generate_reset_token(to_email)
    reset_link = f"{server_url}/reset-password/{token}"  # Secure tokenized link

    # ✉️ HTML email body
    body = f"""
    <html>
        <body>
            <p>Hi,</p>
            <p>You requested a password reset for your Smart Attendance account.</p>
            <p>Click the link below to <a href="{reset_link}">Reset your password</a>.</p>
            <p>This link will expire in 10 minutes for your security.</p>
            <p>If you didn’t request this, please ignore this email.</p>
            <p>Regards,<br>Smart Attendance Team</p>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure connection
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Password reset email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def generate_reset_token(email, expires_sec=600):
    """
    Generates a token for password reset, which will expire in `expires_sec` seconds.
    """
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email, salt=SECURITY_SALT)

def verify_reset_token(token, max_age=600):
    """
    Verifies the reset token. If the token is expired or invalid, returns None.
    """
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = s.loads(token, salt=SECURITY_SALT, max_age=max_age)
    except Exception:
        return None  # Invalid or expired token
    return email

# Simple HTML template for Reset Password Page
reset_password_form = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Reset Password</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(to right, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }

        .reset-container {
            background-color: #ffffff;
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
        }

        h2 {
            text-align: center;
            margin-bottom: 25px;
            color: #333;
        }

        label {
            font-weight: 500;
            display: block;
            margin-bottom: 5px;
        }

        input[type="password"] {
            width: 100%;
            padding: 10px 12px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 12px;
            background-color: #667eea;
            color: white;
            border: none;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #5a67d8;
        }

        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }

        .password-requirements {
            list-style: none;
            padding-left: 0;
            margin-top: 10px;
            font-size: 14px;
        }

        .password-requirements li {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }

        .password-requirements li .checkmark {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid #ccc;
            background-color: white;
        }

        .password-requirements li.valid .checkmark {
            background-color: #4caf50; /* Green for valid */
            border-color: #4caf50;
        }

        .password-requirements li.invalid .checkmark {
            background-color: #f44336; /* Red for invalid */
            border-color: #f44336;
        }

    </style>
</head>
<body>
    <div class="reset-container">
        <h2>Reset Your Password</h2>
        <form id="resetForm" method="POST">
            <input type="hidden" name="email" value="{{ email }}">
            <label>New Password:</label>
            <input type="password" id="password" name="password" required>

            <label>Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>

            <button type="submit" id="submitBtn" disabled>Reset Password</button>

            <ul class="password-requirements">
                <li id="length" class="invalid">
                    <div class="checkmark"></div>
                    Minimum 8 characters
                </li>
                <li id="uppercase" class="invalid">
                    <div class="checkmark"></div>
                    At least one uppercase letter
                </li>
                <li id="special" class="invalid">
                    <div class="checkmark"></div>
                    At least one special character
                </li>
                <li id="digit" class="invalid">
                    <div class="checkmark"></div>
                    At least one digit
                </li>
            </ul>
        </form>
    </div>

    <script>
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        const submitBtn = document.getElementById('submitBtn');
        const requirements = document.querySelectorAll('.password-requirements li');

        function validatePassword() {
            const passwordValue = password.value;

            // Length check
            const lengthValid = passwordValue.length >= 8;
            document.getElementById('length').classList.toggle('valid', lengthValid);
            document.getElementById('length').classList.toggle('invalid', !lengthValid);

            // Uppercase check
            const uppercaseValid = /[A-Z]/.test(passwordValue);
            document.getElementById('uppercase').classList.toggle('valid', uppercaseValid);
            document.getElementById('uppercase').classList.toggle('invalid', !uppercaseValid);

            // Special character check
            const specialValid = /[!@#$%^&*(),.?":{}|<>]/.test(passwordValue);
            document.getElementById('special').classList.toggle('valid', specialValid);
            document.getElementById('special').classList.toggle('invalid', !specialValid);

            // Digit check
            const digitValid = /\d/.test(passwordValue);
            document.getElementById('digit').classList.toggle('valid', digitValid);
            document.getElementById('digit').classList.toggle('invalid', !digitValid);

            // Confirm password check
            if (passwordValue === confirmPassword.value) {
                confirmPassword.setCustomValidity('');
            } else {
                confirmPassword.setCustomValidity('Passwords do not match');
            }

            // Enable submit button if all requirements are met
            submitBtn.disabled = !(lengthValid && uppercaseValid && specialValid && digitValid && passwordValue === confirmPassword.value);
        }

        password.addEventListener('input', validatePassword);
        confirmPassword.addEventListener('input', validatePassword);

        // Prevent form submission if requirements aren't met
        const form = document.getElementById('resetForm');
        form.addEventListener('submit', function (event) {
            if (submitBtn.disabled) {
                event.preventDefault();
                alert('Please make sure your password meets all the requirements.');
            }
        });
    </script>
</body>
</html>


'''



@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        return "Invalid or expired token. Please request a new password reset link."

    if request.method == 'GET':
        # Render the reset password form with the email passed in as context
        return render_template_string(reset_password_form, email=email)

    elif request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if new_password != confirm_password:
            return "Passwords do not match. Please go back and try again."

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        try:
            # Update the password in the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE teachers SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
            cursor.close()
            conn.close()
            return "Password successfully updated! You can now log in with your new password."
        except Exception as e:
            print("Error updating password:", e)
            return "Something went wrong while updating your password. Please try again later."


@app.route('/teacher-info', methods=['GET'])
def get_teacher_info():
    teacher_id = request.args.get('teacher_id')

    if not teacher_id:
        return jsonify({'success': False, 'message': 'Teacher ID is required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch teacher's basic information
        cursor.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
        teacher = cursor.fetchone()

        if not teacher:
            return jsonify({'success': False, 'message': 'Teacher not found'}), 404

        # Fetch subjects assigned to this teacher (subject_code and subject_name)
        cursor.execute("""
            SELECT s.sub_code, s.sub_name
            FROM Teacher_Subject ts
            JOIN Subjects s ON ts.subject_code = s.sub_code
            WHERE ts.teacher_id = %s
        """, (teacher['id'],))
        
        subjects = cursor.fetchall()

        conn.close()

        # Format the response
        response_data = {
            'teacher': {
                'id': teacher['id'],
                'name': teacher['name'],
                'email': teacher['email'],
            },
            'subjects': subjects  # Now we send both code and name
        }

        return jsonify({'success': True, 'data': response_data}), 200

    except Exception as e:
        print(f"Error fetching teacher info: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching data'}), 500



##                          Images will be uploaded on the server using this logic
# Folders
UPLOAD_FOLDER = 'Upload_Folder'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Thread-safe processing queue
from collections import deque
processing_queue = deque()
queue_lock = threading.Lock()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_images', methods=['POST'])
def upload_images():
    subject = request.form.get('subjectCode')
    files = request.files.getlist('images[]')

    # Debugging: Log the subject and received files
    app.logger.debug(f"Received subjectCode: {subject}")
    app.logger.debug(f"Received files: {[file.filename for file in files]}")

    if not subject:
        app.logger.warning("Subject code is missing.")
        return jsonify({'success': False, 'message': 'Subject is required'}), 400

    if not files:
        app.logger.warning("No files uploaded.")
        return jsonify({'success': False, 'message': 'No images uploaded'}), 400

    saved_files = []

    try:
        for index, file in enumerate(files):
            if file and allowed_file(file.filename):
                # Generate a unique filename with more security
                ext = file.filename.rsplit('.', 1)[1].lower()
                timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S-%f')  # Add microseconds for uniqueness
                unique_id = uuid.uuid4().hex[:10]  # Shortened UUID for uniqueness
                new_filename = f"{secure_filename(subject)}_{timestamp}_{index+1}_{unique_id}.{ext}"

                # Save to upload folder
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(upload_path)
                saved_files.append(new_filename)

                # Add to processing queue
                with queue_lock:
                    if upload_path not in processing_queue:  # Prevent duplicates
                        processing_queue.append(upload_path)

                # Debugging: Log the saved file path
                app.logger.debug(f"Saved file: {new_filename} to path: {upload_path}")
            else:
                app.logger.warning(f"File {file.filename} is not allowed or invalid.")

        # If all files are uploaded successfully, respond with success
        return jsonify({
            'success': True,
            'message': f'{len(saved_files)} image(s) uploaded. Processing started.',
            'files': saved_files
        }), 200

    except Exception as e:
        # Cleanup any partially uploaded files
        for f in saved_files:
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f)
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Log the error for debugging
        app.logger.error(f"Upload error: {str(e)}")

        return jsonify({'success': False, 'message': 'Upload failed'}), 500

def extract_subject_from_filename(filename):
    """
    Extracts the subject code from the filename.
    Assumes the subject code is the first part of the filename, before the first underscore.
    Example: 'CS101_image_12345.jpg' -> 'CS101'
    """
    subject_code = filename.split('_')[0]  # Split by underscore and take the first part
    return subject_code

def background_image_processor():
    print("[INFO] Background processor started")
    while True:
        try:
            # Get next file to process
            with queue_lock:
                current_file = processing_queue.popleft() if processing_queue else None

            if current_file:
                if os.path.exists(current_file):
                    try:
                        print(f"[PROCESSING] {os.path.basename(current_file)}")

                        # Process image and get tagged version
                        recognized, tagged_image = recognize_faces_in_image(current_file)

                        # Save tagged image
                        filename = os.path.basename(current_file)
                        attendance_path = os.path.join("Attendance_Records", filename)
                        os.makedirs(os.path.dirname(attendance_path), exist_ok=True)
                        cv2.imwrite(attendance_path, tagged_image)

                        # Extract subject and date from the filename
                        subject_code = extract_subject_from_filename(filename)  # Assume a method to extract subject from filename
                        current_date = datetime.today().strftime('%d-%m-%Y')   # Change date format to ddmmyyyy

                        print(f"Subject Code = {subject_code}")
                        print(f"Date = {current_date}")

                        # Check if students are already marked present for the given subject and date
                        for rollno in recognized:
                            # Ensure that the date column exists before proceeding
                            create_date_column_if_not_exists(subject_code, current_date)

                            # Check if the student is already marked present
                            if not is_student_present(rollno, subject_code, current_date):
                                # Send attendance confirmation email asynchronously
                                send_attendance_emails_async([rollno], subject_code, current_date)
                                # Handle attendance update if not already marked present
                                update_attendance([rollno], subject_code, current_date)

                        # Delete original image after processing
                        os.remove(current_file)

                        print(f"[DONE] Processed {os.path.basename(current_file)}. Recognized: {recognized}")

                    except FileNotFoundError:
                        print(f"[WARNING] File disappeared during processing: {os.path.basename(current_file)}")
                else:
                    print(f"[SKIPPING] Missing file: {os.path.basename(current_file)}")

            time.sleep(0.5)

        except IndexError:
            time.sleep(1)
        except Exception as e:
            print(f"[PROCESSOR ERROR] {str(e)}")
            time.sleep(5)

def is_student_present(rollno, subject_code, date):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        table_name = f"attendance_{subject_code}"  # Dynamically create the table name based on subject code

        cursor.execute(f"SELECT 1 FROM `{table_name}` WHERE rollno = %s AND `{date}` = 1", (rollno,))
        attendance_exists = cursor.fetchone()

        if attendance_exists:
            print(f"[INFO] {rollno} is already marked present for {subject_code} on {date}.")
            return True
        else:
            return False

    except mysql.connector.Error as err:
        print(f"Error checking attendance for {rollno}: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def validate_input(subject_code, date):
    """Validate subject code and date format"""
    if not re.match(r'^[A-Z0-9_]+$', subject_code):
        return False, "Invalid subject code format"
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date):
        return False, "Invalid date format (dd-mm-yyyy)"
    return True, ""



def send_attendance_email(rollno, subject_code, date):
    # Establish database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch student name from students table
        cursor.execute("SELECT Name FROM students WHERE RollNo = %s", (rollno,))
        student_name_result = cursor.fetchone()
        if student_name_result:
            student_name = student_name_result[0]
        else:
            print(f"Student with rollno {rollno} not found.")
            return

        # Fetch subject name from subjects table
        cursor.execute("SELECT sub_name FROM subjects WHERE sub_code = %s", (subject_code,))
        subject_name_result = cursor.fetchone()
        if subject_name_result:
            subject_name = subject_name_result[0]
        else:
            print(f"Subject with code {subject_code} not found.")
            return

        # Check if the student has already been marked present for this subject on this date
        table_name = f"attendance_{subject_code}"  # Dynamically create the table name based on subject code

        # We use the table name as part of the query, so we use it as a formatted string
        cursor.execute(f"SELECT 1 FROM `{table_name}` WHERE rollno = %s AND `{date}` = 1", (rollno,))
        attendance_exists = cursor.fetchone()

        if attendance_exists:
            print(f"[INFO] {rollno} was already marked present for {subject_name} on {date}.")
            return  # Skip sending the email if the student is already marked present

    except mysql.connector.Error as err:
        print(f"Error fetching data from database: {err}")
        return
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Prepare email content
    to_email = f"{rollno}@rgipt.ac.in"
    subject = f"Attendance Confirmation for {subject_name} - {date}"

    # 📧 HTML email body
    body = f"""
    <html>
        <body>
            <p>Dear {student_name},</p>
            <p>You have been marked <strong>present</strong> for the course <strong>{subject_name}</strong> on <strong>{date}</strong>.</p>
            <p>No action is required on your part.</p>
            <p>If you believe this is incorrect, please contact your course instructor.</p>
            <p>Regards,<br>Smart Attendance Team</p>
        </body>
    </html>
    """

    # Sending email
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"[EMAIL SENT] to {to_email}")

    except Exception as e:
        print(f"[EMAIL ERROR] Could not send to {to_email}: {str(e)}")


def send_attendance_emails_async(present_students, subject_code, date):
    def task():
        for rollno in present_students:
            send_attendance_email(rollno, subject_code, date)
    threading.Thread(target=task).start()
    


@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    subject_code = request.args.get('subjectCode')
    date = request.args.get('date')  # Expected format: dd-mm-yyyy
    
    # Input validation
    is_valid, message = validate_input(subject_code, date)
    if not is_valid:
        return jsonify({'success': False, 'message': message}), 200

    table_name = f"Attendance_{subject_code}"
    image_prefix = f"{subject_code}_{date}_"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Subject not found'}), 200

        # Verify date column exists
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE %s", (date,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': "Today's Attendance not found"}), 200

        # Get all students
        cursor.execute(f"SELECT rollno FROM {table_name}")
        all_students = [row[0] for row in cursor.fetchall()]

        # Get present students
        cursor.execute(f"SELECT rollno FROM {table_name} WHERE `{date}` = 1")
        present_students = [row[0] for row in cursor.fetchall()]
        

        # Get tagged images
        image_folder = 'Attendance_Records'
        tagged_images = [
            f for f in os.listdir(image_folder)
            if f.startswith(image_prefix) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]

        return jsonify({
            'success': True,
            'data': present_students,
            'all': all_students,
            'tagged_images': tagged_images
        }), 200

    except mysql.connector.Error as err:
        app.logger.error(f"Database error: {err}")
        return jsonify({'success': False, 'message': 'Database operation failed'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'Server processing error'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/Attendance_Records/<path:filename>')
def serve_tagged_image(filename):
    return send_from_directory('Attendance_Records', filename)




@app.route('/get_all_attendance', methods=['GET'])
def get_all_attendance():
    subject_code = request.args.get('subject_code')  # Match this with the parameter name in the URL
    app.logger.debug(f"Received request for subject_code: {subject_code}")
    
    # Input validation
    if not subject_code:
        app.logger.debug("Subject code is missing.")
        return jsonify({'success': False, 'message': 'Subject code is required'}), 400

    table_name = f"Attendance_{subject_code}"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            app.logger.debug(f"Table {table_name} not found.")
            return jsonify({'success': False, 'message': 'Subject not found'}), 200

        # Get all students (rollno and name) by joining Attendance with Students table
        cursor.execute(f"""
            SELECT S.RollNo, S.Name
            FROM {table_name} A
            JOIN Students S ON A.rollno = S.RollNo
        """)
        all_students = cursor.fetchall()

        # Get all dates (columns except rollno and name)
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()
        dates = [column[0] for column in columns if column[0] != 'rollno']  # Exclude rollno

        # Initialize the result list
        attendance_records = []

        for student in all_students:
            rollno, name = student
            attendance_data = {'roll_number': rollno, 'name': name}
            
            # Get attendance for each date (raw 0 or 1)
            attendance_status = []
            for date in dates:
                cursor.execute(f"SELECT `{date}` FROM {table_name} WHERE rollno = %s", (rollno,))
                status = cursor.fetchone()[0]  # Get attendance status (0 or 1)
                attendance_status.append(status)  # Directly append 0 or 1

            attendance_data['attendance'] = attendance_status
            attendance_records.append(attendance_data)

        # Ensure a response is returned
        if not attendance_records:
            app.logger.debug("No attendance records found.")
            return jsonify({'success': False, 'message': 'No attendance records found'}), 200

        # Return both the dates and the attendance data
        return jsonify({
            'success': True,
            'attendance': attendance_records,
            'dates': dates  # Add the date vector here
        }), 200

    except mysql.connector.Error as err:
        app.logger.error(f"Database error: {err}")
        return jsonify({'success': False, 'message': 'Database operation failed'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'Server processing error'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

        
if __name__ == '__main__':
    # Start background processor
    processor_thread = threading.Thread(target=background_image_processor, daemon=True)
    processor_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)