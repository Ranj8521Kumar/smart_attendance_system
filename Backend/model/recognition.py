# group.py

import face_recognition
import pickle
import cv2
import os

# Load encodings once when the module is imported
with open('model/student_encodings.pkl', 'rb') as f:
    known_encodings, known_names = pickle.load(f)

def recognize_faces_in_image(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, model='hog')
    face_encodings = face_recognition.face_encodings(image, face_locations, model='hog')

    recognized_students = []

    for face_encoding, location in zip(face_encodings, face_locations):
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        min_distance = min(distances)
        min_index = distances.argmin()

        if min_distance < 0.45:
            roll_number = known_names[min_index]
            recognized_students.append(roll_number)

            # Draw tag
            top, right, bottom, left = location
            image = cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            image = cv2.putText(image, roll_number, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Convert for OpenCV saving later (handled by backend)
    bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return recognized_students, bgr_image
