import mysql.connector
import os
import openpyxl
from dotenv import load_dotenv

# Load DB credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def read_rollnos_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    rollnos = []

    if ext == '.txt':
        with open(filepath, 'r') as f:
            rollnos = [line.strip().upper() for line in f if line.strip()]
    elif ext == '.xlsx':
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
            if row[0]:
                rollnos.append(str(row[0]).strip().upper())
    else:
        raise ValueError("Unsupported file type. Use .txt or .xlsx")

    return rollnos

def create_attendance_table(filepath, subject_code):
    table_name = f"Attendance_{subject_code}"
    rollnos = read_rollnos_from_file(filepath)

    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Get valid rollnos from Student_Subject_Enrollment table
    cursor.execute("SELECT rollno FROM Student_Subject_Enrollment")
    valid_rollnos = {row[0].upper() for row in cursor.fetchall()}

    # Create table (if not exists)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            rollno VARCHAR(20),
            PRIMARY KEY (rollno),
            FOREIGN KEY (rollno) REFERENCES Student_Subject_Enrollment(rollno)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """)

    # Track invalid roll numbers
    invalid_rollnos = []

    # Insert only valid rollnos
    for rollno in rollnos:
        if rollno in valid_rollnos:
            cursor.execute(f"INSERT IGNORE INTO {table_name} (rollno) VALUES (%s)", (rollno,))
        else:
            invalid_rollnos.append(rollno)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Table '{table_name}' created/updated with valid roll numbers.")
    if invalid_rollnos:
        print("\n❌ These roll numbers were not found in Student_Subject_Enrollment and were skipped:")
        for r in invalid_rollnos:
            print(" -", r)

# 🧪 Run
if __name__ == "__main__":
    subject_code = input("Enter subject code (e.g., CS101): ").strip().upper()
    filepath = input("Enter path to student roll number file (.txt or .xlsx): ").strip()

    create_attendance_table(filepath, subject_code)
