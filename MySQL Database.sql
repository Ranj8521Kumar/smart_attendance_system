create database smart_attendance_system ;
use smart_attendance_system;

CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
);


select * from teachers ;
 delete from teachers where id = 5 ;


SELECT * FROM teachers WHERE email = '22it3025@rgipt.ac.in';

CREATE TABLE Subjects (
    sub_code VARCHAR(20) PRIMARY KEY,
    sub_name VARCHAR(150) NOT NULL UNIQUE
);


SELECT * FROM subjects WHERE teacher_id = 6;


INSERT INTO Subjects (sub_code, sub_name) VALUES 
('CS101', 'Computer Programming'),
('CS102', 'Computer Engineering Practices'),
('CS201', 'Discrete Mathematics'),
('CS211', 'Data Structure and Algorithm'),
('CS212', 'Database Management Systems'),
('CS223', 'Principles of Programming Languages'),
('CS224', 'Object Oriented Methodologies'),
('CS231', 'Computer Organization and Architecture'),
('CS311', 'Operating Systems'),
('CS312', 'Compiler Design'),
('CS321', 'Theory of Computation'),
('CS331', 'Software Engineering'),
('CS341', 'Design and Analysis of Algorithms'),
('CS351', 'Computer Networks'),
('CS360', 'Artificial Intelligence'),
('CS368', 'Cognition and Cognitive System'),
('CS371', 'Digital Communication System'),
('CS372', 'Wireless Sensor Network'),
('CS382', 'Remote Sensing and Aerial Photogrammetry'),
('CS383', 'UAV Remote Sensing'),
('CS384', 'GPS and Adjustment Computation'),
('CS391', 'Operations Research'),
('CS411', 'Mobile Computing'),
('CS431', 'Cyber Security'),
('CS454', 'Computer Vision and Pattern Recognition'),
('CS457', 'Data Analytics'),
('CS458', 'Data Mining'),
('CS466', 'Natural Language Processing'),
('CS467', 'Robotics'),
('CS468', 'Soft Computing'),
('CS481', 'Wireless Digital Communication'),
('CS491', 'Speech and Language Technology'),
('CS492', 'Robot Motion Planning');

select * from Subjects ;

CREATE TABLE Teacher_Subject (
    subject_code VARCHAR(20) PRIMARY KEY,
    teacher_id INT NOT NULL,
    FOREIGN KEY (subject_code) REFERENCES Subjects(sub_code),
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
);

INSERT INTO Teacher_Subject (subject_code, teacher_id) VALUES
('CS101', 6),
('CS102', 6),
('CS201', 6),
('CS212', 6),
('CS311', 6);


select * from Teacher_Subject ;


CREATE TABLE Students (
  RollNo VARCHAR(20) PRIMARY KEY,
  Name VARCHAR(200),
  Email VARCHAR(50),
  Branch VARCHAR(150),
  Batch VARCHAR(10),
  Image VARCHAR(255)
);

INSERT INTO Students (RollNo, Name, Email, Branch, Batch, Image) VALUES
('22IT3001', 'Aayush Kumar', '22IT3001@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3002', 'Aditya Kumar', '22IT3002@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3003', 'Akshat Goyal', '22IT3003@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3004', 'Aman Anand', '22IT3004@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3005', 'Aman Kumar Gupta', '22IT3005@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3006', 'Amrutkar Tanmay Prashant', '22IT3006@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3008', 'Anushka Nema', '22IT3008@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3009', 'Arnav Sao', '22IT3009@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3010', 'Aryan Kumar Singh', '22IT3010@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3011', 'Astitva Pathak', '22IT3011@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3012', 'Atul Panwar', '22IT3012@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3013', 'Ayush Srivastava', '22IT3013@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3015', 'Himanshu Jayant', '22IT3015@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3016', 'Himanshu Kumar', '22IT3016@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3017', 'Ishuman', '22IT3017@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3018', 'Jagriti Priya', '22IT3018@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3019', 'Kaushal Kumar', '22IT3019@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3020', 'Krishanu Mishra', '22IT3020@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3021', 'Krishna Goyal', '22IT3021@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3022', 'Kriti Mehrotra', '22IT3022@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3023', 'Lavanya Singh', '22IT3023@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3024', 'Mahesh Kumar', '22IT3024@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3025', 'Naresh Kumar', '22IT3025@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3026', 'Nikhilesh Raj Singh', '22IT3026@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3027', 'Nitesh Bairwa', '22IT3027@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3028', 'Payal Singh', '22IT3028@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3029', 'Prashant Singh', '22IT3029@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3030', 'Prateek', '22IT3030@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3031', 'Prathamesh Dhote', '22IT3031@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3032', 'Priyanshu Kumar', '22IT3032@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3033', 'Pushpendra Singh Dangi', '22IT3033@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3034', 'Rajat Kumar', '22IT3034@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3035', 'Rajat Kumar Behera', '22IT3035@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3036', 'Rajnish Kumar', '22IT3036@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3037', 'Ranjan Kumar Pandit', '22IT3037@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3038', 'Rishi Jain', '22IT3038@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3039', 'Rishika Srivastava', '22IT3039@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3040', 'Rohit Sharma', '22IT3040@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3041', 'Saksham Goyal', '22IT3041@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3042', 'Sarthak Raj', '22IT3042@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3043', 'Saurabh Kumar', '22IT3043@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3044', 'Saurabh Pandey', '22IT3044@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3045', 'Shangana Yadav', '22IT3045@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3046', 'Shikhar', '22IT3046@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3047', 'Shivansh Singh', '22IT3047@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3048', 'Shivanshu Kashyap', '22IT3048@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3049', 'Shreyas Prashant Urade', '22IT3049@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3050', 'Shriansh Mishra', '22IT3050@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3051', 'Shubham Kumar', '22IT3051@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3052', 'Siddharth Chhoria', '22IT3052@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3055', 'Srishti Tripathi', '22IT3055@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3056', 'Suruchi Kumari', '22IT3056@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3057', 'Swayanshu Rout', '22IT3057@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3058', 'Telange Khandeshwar Govind', '22IT3058@rgipt.ac.in', 'Information Technology', '2022', ''),
('22IT3059', 'Yash Verma', '22IT3059@rgipt.ac.in', 'Information Technology', '2022', '');

select * from Students;

CREATE TABLE Student_Subject_Enrollment (
  rollno VARCHAR(20),
  subject_code VARCHAR(20),
  PRIMARY KEY (rollno, subject_code),
  FOREIGN KEY (rollno) REFERENCES Students(RollNo),
  FOREIGN KEY (subject_code) REFERENCES Subjects(sub_code)
);


show tables;
select * from Attendance_CS101;

ALTER TABLE Attendance_CS101
DROP COLUMN `2025-04-22 00:00:00`;

