from app.db import get_db_connection, close_connection
from werkzeug.security import generate_password_hash, check_password_hash

class Teacher:
    def __init__(self, t_id=None, name=None, email=None, password=None):
        self.t_id = t_id
        self.name = name
        self.email = email
        self.password = password

    @staticmethod
    def get_by_email(email):
        """
        Get teacher by email
        """
        connection = get_db_connection()
        if not connection:
            print("Database connection failed in get_by_email")
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM Teachers WHERE email = %s"
            print(f"Executing query: {query} with email: {email}")
            cursor.execute(query, (email,))
            teacher_data = cursor.fetchone()

            print(f"Teacher data retrieved: {teacher_data}")

            if teacher_data:
                # Check for key errors
                print(f"Keys in teacher_data: {teacher_data.keys()}")

                # Try different possible column names
                # For t_id
                t_id = None
                for key in ['t_id', 'id', 'teacher_id', 'tid']:
                    if key in teacher_data:
                        t_id = teacher_data[key]
                        print(f"Found t_id as '{key}': {t_id}")
                        break

                # For name
                name = None
                for key in ['Name', 'name', 'teacher_name']:
                    if key in teacher_data:
                        name = teacher_data[key]
                        print(f"Found name as '{key}': {name}")
                        break

                # For email
                email = None
                for key in ['email', 'Email', 'teacher_email']:
                    if key in teacher_data:
                        email = teacher_data[key]
                        print(f"Found email as '{key}': {email}")
                        break

                # For password
                password = None
                for key in ['password', 'Password', 'teacher_password']:
                    if key in teacher_data:
                        password = teacher_data[key]
                        print(f"Found password as '{key}': {password}")
                        break

                print(f"Creating Teacher object with: t_id={t_id}, name={name}, email={email}")

                return Teacher(
                    t_id=t_id,
                    name=name,
                    email=email,
                    password=password
                )
            print(f"No teacher found with email: {email}")
            return None
        except Exception as e:
            print(f"Error retrieving teacher: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def verify_password(email, password):
        """
        Verify teacher's password using Werkzeug's password hashing
        """
        connection = get_db_connection()
        if not connection:
            print("Database connection failed")
            return False

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM Teachers WHERE email = %s"
            cursor.execute(query, (email,))
            teacher = cursor.fetchone()

            if teacher:
                # Debug: Print teacher data
                print(f"Teacher found: {teacher}")

                # Try to get email from different possible column names
                email_value = None
                for key in ['email', 'Email', 'teacher_email']:
                    if key in teacher:
                        email_value = teacher[key]
                        print(f"Found email as '{key}': {email_value}")
                        break

                # Try to get password from different possible column names
                stored_password = None
                for key in ['password', 'Password', 'teacher_password']:
                    if key in teacher:
                        stored_password = teacher[key]
                        print(f"Found password as '{key}': {stored_password}")
                        break

                print(f"Input password: {password}")

                # Check if the stored password is actually hashed
                if stored_password:
                    # Check for different hash formats
                    if stored_password.startswith('pbkdf2:sha256:') or stored_password.startswith('scrypt:'):
                        print(f"Password appears to be hashed with format: {stored_password.split(':')[0]}")
                        try:
                            result = check_password_hash(stored_password, password)
                            print(f"Password verification result: {result}")
                            return result
                        except Exception as e:
                            print(f"Error checking password hash: {e}")
                            # Fall back to direct comparison if hash check fails
                            result = (stored_password == password)
                            print(f"Falling back to direct comparison: {result}")
                            return result
                    else:
                        print("WARNING: Password does not appear to be in a recognized hash format!")
                        print("Falling back to direct comparison")
                        result = (stored_password == password)
                        print(f"Direct comparison result: {result}")
                        return result
                else:
                    print("No password stored for this user!")
                    return False
            else:
                print(f"No teacher found with email: {email}")
            return False
        except Exception as e:
            print(f"Error verifying password: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def hash_password(password):
        """
        Hash a password using Werkzeug's password hashing
        """
        return generate_password_hash(password)
