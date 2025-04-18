import os
import mysql.connector
from dotenv import load_dotenv
import secrets
import string
from werkzeug.security import generate_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env variables
load_dotenv()

# Config
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))

# Generate random secure password
def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

# Send email
def send_password_email(to_email, name, password):
    subject = "Your Smart Attendance System Login Password"
    body = f"""
    Hello {name},

    You have been registered on the Smart Attendance System.

    Email: {to_email}
    Password: {password}

    Please change your password after your first login.

    Regards,
    Smart Attendance Team
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("📧 Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)

# Insert into DB
def insert_teacher(name, email):
    plain_pwd = generate_password()
    hashed_pwd = generate_password_hash(plain_pwd)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
        INSERT INTO teachers (name, email, password)
        VALUES (%s, %s, %s)
    """
    values = (name, email, hashed_pwd)
    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    # Send email
    send_password_email(email, name, plain_pwd)

    print("\n✅ Teacher added successfully.")
    print("✅ Password sent via email.\n")

# Main prompt
if __name__ == "__main__":
    name = input("Enter teacher name: ")
    email = input("Enter teacher email (must be @rgipt.ac.in): ")

    if not email.endswith("@rgipt.ac.in"):
        print("❌ Invalid email domain. Use @rgipt.ac.in only.")
    else:
        insert_teacher(name, email)
