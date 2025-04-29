from app.db import get_db_connection, close_connection
from app.config import DB_CONFIG

class Analytics:
    @staticmethod
    def get_batches():
        """
        Get all unique batches
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor()
            query = "SELECT DISTINCT Batch FROM Students ORDER BY Batch"
            cursor.execute(query)
            batches = [batch[0] for batch in cursor.fetchall()]
            return batches
        except Exception as e:
            print(f"Error retrieving batches: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_branches():
        """
        Get all unique branches
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor()
            query = "SELECT DISTINCT Branch FROM Students ORDER BY Branch"
            cursor.execute(query)
            branches = [branch[0] for branch in cursor.fetchall()]
            return branches
        except Exception as e:
            print(f"Error retrieving branches: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_subjects():
        """
        Get all subjects
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT sub_code, sub_name FROM Subjects ORDER BY sub_name"
            cursor.execute(query)
            subjects = cursor.fetchall()
            return subjects
        except Exception as e:
            print(f"Error retrieving subjects: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_batch_analytics():
        """
        Get analytics data by batch
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT Batch, COUNT(*) as total_students,
                       (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Students)) as percentage
                FROM Students
                GROUP BY Batch
                ORDER BY Batch
            """
            cursor.execute(query)
            batch_data = cursor.fetchall()
            return batch_data
        except Exception as e:
            print(f"Error retrieving batch analytics: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_branch_analytics(batch=None):
        """
        Get analytics data by branch, optionally filtered by batch
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            if batch:
                query = """
                    SELECT Branch, COUNT(*) as total_students,
                           (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Students WHERE Batch = %s)) as percentage
                    FROM Students
                    WHERE Batch = %s
                    GROUP BY Branch
                    ORDER BY Branch
                """
                cursor.execute(query, (batch, batch))
            else:
                query = """
                    SELECT Branch, COUNT(*) as total_students,
                           (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Students)) as percentage
                    FROM Students
                    GROUP BY Branch
                    ORDER BY Branch
                """
                cursor.execute(query)
            branch_data = cursor.fetchall()
            return branch_data
        except Exception as e:
            print(f"Error retrieving branch analytics: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_subject_analytics(batch=None, branch=None):
        """
        Get analytics data by subject, optionally filtered by batch and branch
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            params = []
            where_clause = ""

            if batch and branch:
                where_clause = "WHERE s.Batch = %s AND s.Branch = %s"
                params = [batch, branch]
            elif batch:
                where_clause = "WHERE s.Batch = %s"
                params = [batch]
            elif branch:
                where_clause = "WHERE s.Branch = %s"
                params = [branch]

            query = f"""
                SELECT sub.sub_code, sub.sub_name, COUNT(sse.rollno) as enrolled_students,
                       (COUNT(sse.rollno) * 100.0 / (
                           SELECT COUNT(*) FROM Students s2 {where_clause}
                       )) as percentage
                FROM Subjects sub
                LEFT JOIN Student_Subject_Enrollment sse ON sub.sub_code = sse.subject_code
                LEFT JOIN Students s ON sse.rollno = s.RollNo
                {where_clause}
                GROUP BY sub.sub_code, sub.sub_name
                ORDER BY sub.sub_name
            """
            cursor.execute(query, params * 2 if params else [])
            subject_data = cursor.fetchall()
            return subject_data
        except Exception as e:
            print(f"Error retrieving subject analytics: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_student_analytics(batch=None, branch=None, subject=None):
        """
        Get student data, optionally filtered by batch, branch, and subject
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            query_parts = ["SELECT s.RollNo, s.Name, s.Branch, s.Batch FROM Students s"]
            params = []

            # Build WHERE clause based on filters
            where_clauses = []
            if batch:
                where_clauses.append("s.Batch = %s")
                params.append(batch)
            if branch:
                where_clauses.append("s.Branch = %s")
                params.append(branch)
            if subject:
                query_parts.append("JOIN Student_Subject_Enrollment sse ON s.RollNo = sse.rollno")
                where_clauses.append("sse.subject_code = %s")
                params.append(subject)

            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))

            query_parts.append("ORDER BY s.RollNo")
            query = " ".join(query_parts)

            cursor.execute(query, params)
            students = cursor.fetchall()
            return students
        except Exception as e:
            print(f"Error retrieving student analytics: {e}")
            return []
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_student_attendance(subject_code, rollno=None):
        """
        Get attendance data for a specific subject, optionally filtered by roll number
        """
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)

            # First check if the table exists
            check_query = f"""
                SELECT COUNT(*) as table_exists
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            """
            cursor.execute(check_query, (DB_CONFIG['database'], subject_code))
            result = cursor.fetchone()

            if not result or result['table_exists'] == 0:
                return []

            # Get the column names (dates) from the table
            columns_query = f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME != 'rollno'
                ORDER BY ORDINAL_POSITION
            """
            cursor.execute(columns_query, (DB_CONFIG['database'], subject_code))
            date_columns = [col['COLUMN_NAME'] for col in cursor.fetchall()]

            # Build the query to get attendance data
            columns_str = ", ".join([f"`{col}`" for col in date_columns])
            query = f"SELECT rollno, {columns_str} FROM `{subject_code}`"

            if rollno:
                query += " WHERE rollno = %s"
                cursor.execute(query, (rollno,))
            else:
                cursor.execute(query)

            attendance_data = cursor.fetchall()

            # Format the result to include dates
            formatted_data = {
                'dates': date_columns,
                'attendance': attendance_data
            }

            return formatted_data
        except Exception as e:
            print(f"Error retrieving attendance data: {e}")
            return []
        finally:
            close_connection(connection, cursor)
