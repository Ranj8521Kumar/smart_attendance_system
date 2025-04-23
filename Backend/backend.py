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
import shutil
import uuid
import threading
import time
import cv2
from attendance_update import handle_attendance_update
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS




# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)


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

    if not email.endswith('@rgipt.ac.in'):
        return jsonify({'success': False, 'message': 'Email must end with @rgipt.ac.in'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        # Exclude password from being returned for safety
        user.pop('password', None)
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

    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()

    if user:
        try:
            send_reset_email(email)
            return jsonify({'success': True, 'message': f'Reset link sent to {email}'}), 200
        except Exception as e:
            print(f"Error sending email: {e}")
            return jsonify({'success': False, 'message': 'Failed to send email'}), 500
    else:
        return jsonify({'success': False, 'message': 'Email not found'}), 404


def send_reset_email(to_email):
    sender = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    
    

    subject = "Reset Your Smart Attendance Password"
    
    reset_link = f"http://192.168.25.109:5000/reset-password?email={to_email}"  # Replace with your app link
    
    # HTML email body
    body = f"""
    <html>
        <body>
            <p>Hi,</p>
            <p>You requested a password reset for your Smart Attendance account.</p>
            <p>Click the link below to <a href="{reset_link}">Reset your password</a>.</p>
            <p>If you didn’t request this, please ignore this email.</p>
            <p>Regards,<br>Smart Attendance Team</p>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach HTML part
    msg.attach(MIMEText(body, "html"))  # Set MIME type to HTML


    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

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
        <form method="POST">
            <input type="hidden" name="email" value="{{ email }}">
            <label>New Password:</label>
            <input type="password" id="password" name="password" required>

            <label>Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>

            <button type="submit">Reset Password</button>

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
        }

        password.addEventListener('input', validatePassword);
        confirmPassword.addEventListener('input', validatePassword);
    </script>
</body>
</html>

'''



@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        email = request.args.get('email')
        return render_template_string(reset_password_form, email=email)

    elif request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return "Passwords do not match. Please go back and try again."

        # ✅ Hash the password before storing it
        hashed_password = generate_password_hash(new_password)

        try:
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

                        # Handle attendance update
                        subject_code = extract_subject_from_filename(filename)  # Assume a method to extract subject from filename
                        current_date = datetime.today().strftime('%d-%m-%Y')   # Change date format to ddmmyyyy
                        print(f"Subject Code = {subject_code}")
                        print(f"Date = {current_date}")
                        handle_attendance_update(recognized, subject_code, current_date)

                        # Delete original image
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


@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    subject_code = request.args.get('subjectCode')
    date = request.args.get('date')  # format: dd-mm-yyyy
    formatted_date = date.replace('-', '_')  # match file naming convention

    if not subject_code or not date:
        return jsonify({'success': False, 'message': 'Subject code and date are required'}), 400

    table_name = f"Attendance_{subject_code}"
    image_prefix = f"{subject_code}_{date}_"
    image_folder = 'Attendance_Records'

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': f"Table {table_name} not found."}), 404

        # Check if date column exists
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{formatted_date}'")
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': f"Column for date {date} not found."}), 404

        # Fetch all students
        cursor.execute(f"SELECT rollno FROM {table_name}")
        all_students = [row[0] for row in cursor.fetchall()]

        # Fetch present students
        cursor.execute(f"SELECT rollno FROM {table_name} WHERE `{date}` = 1")
        present_students = [row[0] for row in cursor.fetchall()]

        # Fetch image filenames
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
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/Attendance_Records/<filename>')
def serve_tagged_image(filename):
    return send_from_directory('Attendance_Records', filename)
        
        
if __name__ == '__main__':
    # Start background processor
    processor_thread = threading.Thread(target=background_image_processor, daemon=True)
    processor_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)