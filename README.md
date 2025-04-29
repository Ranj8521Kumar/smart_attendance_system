# Smart Attendance System

A modern, face recognition-based attendance management system designed for educational institutions. This system automates the attendance tracking process using facial recognition technology, making it efficient, accurate, and tamper-proof.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Database Setup](#database-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

The Smart Attendance System is designed to revolutionize traditional attendance tracking methods in educational institutions. By leveraging facial recognition technology, the system automatically identifies students in classroom images and marks their attendance, eliminating the need for manual roll calls and reducing administrative overhead.

The system consists of two main applications:
- **Teacher Application**: Allows teachers to manage classes, take attendance through image uploads, and view attendance records
- **Student Application**: Enables students to view their attendance status across different courses

## ✨ Features

### Teacher Application
- Secure login system for teachers
- Dashboard to view and manage assigned courses
- Upload classroom images for automated attendance marking
- View attendance records by date and subject
- View tagged images showing recognized students
- Password reset functionality

### Student Application
- Student login portal
- View attendance status across enrolled courses
- Check attendance history

### Backend System
- Face recognition using state-of-the-art algorithms
- Automated attendance marking based on recognized faces
- Secure database for storing student and attendance records
- Email notifications for account creation and password resets

## 🏗️ System Architecture

The system follows a client-server architecture:

1. **Frontend**: Flutter-based mobile applications for teachers and students
2. **Backend**: Flask-based REST API server handling business logic and face recognition
3. **Database**: MySQL database for storing user data, course information, and attendance records

## 🛠️ Technologies Used

### Frontend
- Flutter (Dart) for cross-platform mobile application development
- HTTP package for API communication
- Shared Preferences for local storage
- Image Picker for capturing/selecting images

### Backend
- Python Flask for the REST API server
- face_recognition library for facial recognition
- OpenCV for image processing
- MySQL Connector for database operations
- Threading for background image processing
- SMTP for email notifications

### Database
- MySQL for relational data storage

## 📥 Installation

### Prerequisites
- Python 3.8+ with pip
- Flutter SDK 3.5+
- MySQL Server 8.0+
- Git

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-attendance-system.git
   cd smart-attendance-system
   ```

2. Set up a Python virtual environment:
   ```bash
   cd Backend
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install flask mysql-connector-python python-dotenv face-recognition opencv-python flask-cors
   ```

4. Create a `.env` file in the Backend directory with the following variables:
   ```
   DB_HOST=localhost
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_NAME=smart_attendance_system
   
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   ```

5. Create a `database` folder in the Backend directory to store student face images.

6. Run the encoding script to create face encodings:
   ```bash
   python model/encode.py
   ```

7. Start the Flask server:
   ```bash
   python backend.py
   ```

### Frontend Setup

#### Teacher Application

1. Navigate to the teacher application directory:
   ```bash
   cd Frontend/teacher_version
   ```

2. Create a `.env` file with the server URL:
   ```
   SERVER_URL=http://your_server_ip:5000
   ```

3. Install Flutter dependencies:
   ```bash
   flutter pub get
   ```

4. Run the application:
   ```bash
   flutter run
   ```

#### Student Application

1. Navigate to the student application directory:
   ```bash
   cd Frontend/student_version
   ```

2. Install Flutter dependencies:
   ```bash
   flutter pub get
   ```

3. Run the application:
   ```bash
   flutter run
   ```

### Database Setup

1. Create the MySQL database and tables using the provided SQL script:
   ```bash
   mysql -u your_username -p < "MySQL Database.sql"
   ```

2. Alternatively, you can run the SQL commands directly in MySQL Workbench or another MySQL client.

## 🚀 Usage

### Teacher Application

1. Log in with your institutional email (must end with @rgipt.ac.in) and password
2. From the dashboard, select a subject to manage attendance
3. Upload classroom images to automatically mark attendance
4. View attendance records by date
5. Check tagged images showing recognized students

### Student Application

1. Log in with your student credentials
2. View your attendance status across all enrolled courses
3. Check detailed attendance history

## 📁 Project Structure

```
Smart Attendance System/
├── Backend/
│   ├── model/
│   │   ├── encode.py          # Script to encode student faces
│   │   └── recognition.py     # Face recognition implementation
│   ├── database/              # Folder for student face images
│   ├── Attendance_Records/    # Folder for tagged attendance images
│   ├── Upload_Folder/         # Temporary storage for uploaded images
│   ├── backend.py             # Main Flask application
│   ├── attendance_update.py   # Attendance processing logic
│   ├── create_attendance_table.py # Script to create attendance tables
│   ├── db_config.py           # Database configuration
│   └── insert_teacher_data.py # Script to add teacher accounts
│
├── Frontend/
│   ├── teacher_version/       # Flutter app for teachers
│   │   ├── lib/
│   │   │   ├── main.dart      # Entry point
│   │   │   ├── login.dart     # Login screen
│   │   │   ├── home.dart      # Dashboard
│   │   │   └── ...
│   │   └── ...
│   │
│   └── student_version/       # Flutter app for students
│       ├── lib/
│       │   ├── main.dart      # Entry point
│       │   └── ...
│       └── ...
│
└── MySQL Database.sql         # Database schema
```

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
