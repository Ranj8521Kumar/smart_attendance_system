import mysql.connector
from mysql.connector import Error
from app.config import DB_CONFIG

def create_database():
    """
    Create the database and tables
    """
    connection = None
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            print(f"Database '{DB_CONFIG['database']}' created or already exists")

            # Switch to the database
            cursor.execute(f"USE {DB_CONFIG['database']}")

            # Create Teachers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Teachers (
                    t_id INT AUTO_INCREMENT PRIMARY KEY,
                    Name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            """)
            print("Teachers table created or already exists")

            # Create Subjects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Subjects (
                    sub_code VARCHAR(20) PRIMARY KEY,
                    sub_name VARCHAR(150) NOT NULL UNIQUE
                )
            """)
            print("Subjects table created or already exists")

            # Create Teacher_Subject table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Teacher_Subject (
                    teacher_id INT NOT NULL,
                    subject_code VARCHAR(20) NOT NULL,
                    PRIMARY KEY (subject_code),
                    FOREIGN KEY (teacher_id) REFERENCES Teachers(t_id),
                    FOREIGN KEY (subject_code) REFERENCES Subjects(sub_code)
                )
            """)
            print("Teacher_Subject table created or already exists")

            # Create Students table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Students (
                    RollNo VARCHAR(20) PRIMARY KEY,
                    Name VARCHAR(200),
                    Email VARCHAR(50),
                    Branch VARCHAR(150),
                    Batch VARCHAR(10),
                    Image VARCHAR(255)
                )
            """)
            print("Students table created or already exists")

            # Create Student_Credentials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Student_Credentials (
                    rollno VARCHAR(20) PRIMARY KEY,
                    email VARCHAR(50),
                    password VARCHAR(200),
                    FOREIGN KEY (rollno) REFERENCES Students(RollNo)
                )
            """)
            print("Student_Credentials table created or already exists")

            # Create Student_Subject_Enrollment table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Student_Subject_Enrollment (
                    rollno VARCHAR(20),
                    subject_code VARCHAR(20),
                    PRIMARY KEY (rollno, subject_code),
                    FOREIGN KEY (rollno) REFERENCES Students(RollNo),
                    FOREIGN KEY (subject_code) REFERENCES Subjects(sub_code)
                )
            """)
            print("Student_Subject_Enrollment table created or already exists")

            # Create sample subject tables for attendance
            subject_codes = ['CS312', 'CS331', 'CS351', 'MT483', 'CS458']
            for subject_code in subject_codes:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {subject_code} (
                        rollno VARCHAR(20) PRIMARY KEY,
                        FOREIGN KEY (rollno) REFERENCES Students(RollNo)
                    )
                """)
                print(f"{subject_code} table created or already exists")

            # The database already contains data, so we won't insert any new data
            # Just print a message to confirm
            print("Database setup complete. Using existing data.")

            connection.commit()

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_database()
