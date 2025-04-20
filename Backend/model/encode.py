# encode_students.py
import face_recognition
import os
import pickle

# Folder with student images named as <rollno>.jpg
image_folder = "database"
known_encodings = []
known_names = []

for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.jpg', '.png')):
        filepath = os.path.join(image_folder, filename)
        image = face_recognition.load_image_file(filepath)

        # Use CNN for better accuracy
        encodings = face_recognition.face_encodings(image, model='hog')
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])  # roll no

# Save encodings
with open('student_encodings.pkl', 'wb') as f:
    pickle.dump((known_encodings, known_names), f)

print("Database encoding completed and saved.")
