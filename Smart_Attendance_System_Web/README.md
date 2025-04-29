# Smart Attendance System

A web-based system for managing and analyzing student attendance.

## Features

- Teacher login
- Analytics dashboard with filtering capabilities
- Batch-wise, branch-wise, and subject-wise analytics
- Student attendance tracking

## Prerequisites

- Python 3.7+
- MySQL

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smart-attendance-system.git
   cd smart-attendance-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure the database:
   - Create a MySQL database
   - Update the `.env` file with your database credentials

5. Set up the database:
   ```
   python setup_db.py
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the application at `http://localhost:5000`

## Usage

1. Log in with the following credentials:
   - Email: john.doe@example.com
   - Password: password123

2. Use the filters to view different analytics:
   - Batch filter: View branch-wise analytics for a specific batch
   - Batch + Branch filter: View subject-wise analytics for a specific batch and branch
   - Batch + Branch + Subject filter: View student attendance for a specific batch, branch, and subject

## Project Structure

```
smart-attendance-system/
├── app/
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   └── analytics_controller.py
│   ├── models/
│   │   ├── teacher.py
│   │   └── analytics.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   ├── templates/
│   │   ├── 404.html
│   │   ├── 500.html
│   │   ├── analytics.html
│   │   ├── analytics_branches.html
│   │   ├── analytics_student_attendance.html
│   │   ├── analytics_subjects.html
│   │   ├── base.html
│   │   └── home.html
│   ├── config.py
│   └── db.py
├── .env
├── app.py
├── README.md
├── requirements.txt
└── setup_db.py
```
