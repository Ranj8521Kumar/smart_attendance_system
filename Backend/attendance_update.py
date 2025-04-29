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

# MySQL Connection using env variables
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def create_date_column_if_not_exists(subject_code, current_date):
    """
    Checks if the date column exists in the attendance table.
    If it doesn't, it creates the column and sets all values to 0 (absent).
    """

    # Convert current_date (string) to a datetime object
    current_date = datetime.strptime(current_date, '%d-%m-%Y')
    formatted_date = current_date.strftime('%d-%m-%Y')

    # Connect to the MySQL database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        table_name = f"attendance_{subject_code}"

        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            print(f"[ERROR] Attendance table for {subject_code} does not exist. Skipping column creation.")
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

            # Set all values in this column to 0 (absent)
            cursor.execute(f"UPDATE {table_name} SET `{formatted_date}` = 0")
            print(f"[INFO] Set all attendance records for `{formatted_date}` to 0 (absent).")

        # Commit changes
        conn.commit()

    except mysql.connector.Error as err:
        print(f"[ERROR] MySQL Error: {str(err)}")
    except Exception as e:
        print(f"[ERROR] Error in creating date column: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_attendance(recognized, subject_code, current_date):
    """
    Marks the attendance of recognized students as present (1) for the specified subject and date.
    """

    # Convert current_date (string) to a datetime object
    current_date = datetime.strptime(current_date, '%d-%m-%Y')
    formatted_date = current_date.strftime('%d-%m-%Y')

    # Connect to the MySQL database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        table_name = f"attendance_{subject_code}"

        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            print(f"[ERROR] Attendance table for {subject_code} does not exist. Skipping attendance update.")
            return

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

    except mysql.connector.Error as err:
        print(f"[ERROR] MySQL Error: {str(err)}")
    except Exception as e:
        print(f"[ERROR] Error in updating attendance: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
