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

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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

        # Fetch subjects assigned to this teacher
        cursor.execute("SELECT subject_code FROM Teacher_subject WHERE teacher_id = %s", (teacher['id'],))
        subjects = [row['subject_code'] for row in cursor.fetchall()]

        conn.close()

        # Format the response
        response_data = {
            'teacher': {
                'id': teacher['id'],
                'name': teacher['name'],
                'email': teacher['email'],
            },
            'subjects': subjects
        }

        return jsonify({'success': True, 'data': response_data}), 200

    except Exception as e:
        print(f"Error fetching teacher info: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching data'}), 500


##                          Images will be uploaded on the server using this logic

# Folders
UPLOAD_FOLDER = 'Upload_Folder'
PROCESSED_FOLDER = 'Processed_Folder'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_images', methods=['POST'])
def upload_images():
    subject = request.form.get('subject')
    files = request.files.getlist('images[]')  # Multiple file input

    if not subject:
        return jsonify({'success': False, 'message': 'Subject is required'}), 400

    if not files:
        return jsonify({'success': False, 'message': 'No images uploaded'}), 400

    saved_files = []
    all_recognized_students = []

    try:
        for index, file in enumerate(files):
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
                unique_id = uuid.uuid4().hex[:6]
                new_filename = f"{secure_filename(subject)}_{timestamp}_{index+1}_{unique_id}.{ext}"

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(filepath)
                saved_files.append(new_filename)

                # Process image (face recognition)
                recognized = recognize_faces_in_image(filepath)
                all_recognized_students.extend(recognized)

                # Move processed image to record folder
                processed_path = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
                shutil.move(filepath, processed_path)

        return jsonify({
            'success': True,
            'message': f'{len(saved_files)} image(s) uploaded and processed.',
            'files': saved_files,
            'recognized_students': list(set(all_recognized_students))  # remove duplicates
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'}), 500


import threading
import time

def background_image_processor():
    print("[INFO] Background image processor started.")
    while True:
        try:
            files = os.listdir(UPLOAD_FOLDER)
            image_files = [f for f in files if allowed_file(f)]

            for filename in image_files:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                print(f"[PROCESSING] {filename}")

                recognized = recognize_faces_in_image(filepath)

                # Move to processed folder
                processed_path = os.path.join(PROCESSED_FOLDER, filename)
                shutil.move(filepath, processed_path)

                print(f"[DONE] Moved {filename} to {PROCESSED_FOLDER}. Recognized: {recognized}")

        except Exception as e:
            print(f"[ERROR in background processor]: {e}")

        time.sleep(5)  # check every 5 seconds


if __name__ == '__main__':
    processor_thread = threading.Thread(target=background_image_processor, daemon=True)
    processor_thread.start()

    app.run(host='0.0.0.0', port=5000, debug=True)

