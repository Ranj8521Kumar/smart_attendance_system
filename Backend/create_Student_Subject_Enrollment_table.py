from backend import get_db_connection
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

def create_student_subject_enrollment_for_batch(filepath, subject_codes):
    rollnos = read_rollnos_from_file(filepath)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get valid rollnos from Students table
    cursor.execute("SELECT RollNo FROM Students")
    valid_rollnos = {row[0].upper() for row in cursor.fetchall()}

    # Get valid subject codes from Subjects table
    cursor.execute("SELECT sub_code FROM Subjects")
    valid_subject_codes = {row[0].upper() for row in cursor.fetchall()}

    # Create the Student_Subject_Enrollment table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS Student_Subject_Enrollment (
            rollno VARCHAR(20),
            subject_code VARCHAR(20),
            PRIMARY KEY (rollno, subject_code),
            FOREIGN KEY (rollno) REFERENCES Students(RollNo)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES Subjects(sub_code)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """)

    # Track invalid roll numbers or subject codes
    invalid_rollnos = []
    invalid_subject_codes = []

    # Insert valid rollno and subject_code pairs for each rollno in batch
    for rollno in rollnos:
        if rollno in valid_rollnos:
            for subject_code in subject_codes:
                if subject_code in valid_subject_codes:
                    cursor.execute(f"INSERT IGNORE INTO Student_Subject_Enrollment (rollno, subject_code) VALUES (%s, %s)", (rollno, subject_code))
                else:
                    invalid_subject_codes.append(subject_code)
        else:
            invalid_rollnos.append(rollno)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Student enrollment for batch completed with valid rollno and subject_code pairs.")
    
    if invalid_rollnos or invalid_subject_codes:
        print("\n❌ Some entries were skipped because they were not found in the respective tables:")
        if invalid_rollnos:
            print(" - Invalid roll numbers (not found in 'Students' table):")
            for r in invalid_rollnos:
                print("   -", r)
        if invalid_subject_codes:
            print(" - Invalid subject codes (not found in 'Subjects' table):")
            for s in invalid_subject_codes:
                print("   -", s)

# 🧪 Run
if __name__ == "__main__":
    filepath = input("Enter path to student roll number file (.txt or .xlsx): ").strip()
    
    # Ask user if they want to add one or more subjects
    subject_codes_input = input("Enter subject code(s) (e.g., CS101 or CS101,MATH102,PHY103): ").strip()
    
    # Split input and convert to uppercase (handling both single and multiple codes)
    subject_codes = [subject_code.strip().upper() for subject_code in subject_codes_input.split(",")]

    create_student_subject_enrollment_for_batch(filepath, subject_codes)
