import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

# Load DB credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def handle_attendance_update(recognized, subject_code, current_date):
    """
    Updates the attendance for recognized students. Adds column if missing.
    Marks 1 for present, 0 for absent.
    """

    # Convert current_date (string) to a datetime object
    current_date = datetime.strptime(current_date, '%d-%m-%Y')  # assuming input date format is 'yyyy-mm-dd'
    
    # Format the date as 'dd-mm-yyyy' for column name
    formatted_date = current_date.strftime('%d-%m-%Y')

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    table_name = f"attendance_{subject_code}"

    try:
        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            print(f"[ERROR] Attendance table for {subject_code} does not exist. Skipping attendance update.")
            return

        # Check if date column exists
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_name = %s AND column_name = %s
        """, (table_name, formatted_date))
        column_exists = cursor.fetchone()[0] == 1

        if not column_exists:
            # Add column if it doesn't exist
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN `{formatted_date}` TINYINT DEFAULT 0")
            print(f"[INFO] Created new date column `{formatted_date}` in {table_name}.")

        # Fetch all roll numbers from the table
        cursor.execute(f"SELECT rollno FROM {table_name}")
        all_students = {row[0] for row in cursor.fetchall()}
        recognized_set = set(recognized)

        # Update attendance for recognized students
        for rollno in recognized:
            try:
                # Check if the rollno exists in the table
                cursor.execute(f"SELECT `{formatted_date}` FROM {table_name} WHERE rollno = %s", (rollno,))
                result = cursor.fetchone()

                if result is not None:
                    current_value = result[0]
                    if current_value == 0 or current_value is None:
                        # Update to 1 (Present)
                        cursor.execute(f"""
                            UPDATE {table_name} 
                            SET `{formatted_date}` = 1 
                            WHERE rollno = %s
                        """, (rollno,))
                        print(f"[PRESENT] {rollno} marked present for {subject_code} on {formatted_date}.")
                    else:
                        print(f"[INFO] {rollno} was already marked present for {subject_code} on {formatted_date}.")
                else:
                    print(f"[WARNING] {rollno} is not in the attendance table for {subject_code}. Skipping.")
            except Exception as e:
                print(f"[ERROR] Could not update attendance for {rollno}: {str(e)}")

        # Commit changes
        conn.commit()

    except Exception as e:
        print(f"[ERROR] Error in attendance update: {str(e)}")
    finally:
        cursor.close()
        conn.close()
