import streamlit as st
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import pandas as pd

KNOWN_FACES_DIR = 'known_faces'
ATTENDANCE_FILE = 'Attendance.csv'

# Function to load and encode images of known people
def load_known_faces():
    known_faces = []
    known_names = []
    for name in os.listdir(KNOWN_FACES_DIR):
        if os.path.isdir(os.path.join(KNOWN_FACES_DIR, name)):
            for filename in os.listdir(os.path.join(KNOWN_FACES_DIR, name)):
                image_path = os.path.join(KNOWN_FACES_DIR, name, filename)
                if os.path.isfile(image_path):
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        encoding = encodings[0]
                        known_faces.append(encoding)
                        known_names.append(name)
    return known_faces, known_names

# Function to mark attendance
def mark(name):
    with open(ATTENDANCE_FILE, 'a') as f:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{name},Present,{dt_string}\n')

# Function to process video frames and recognize faces
def process_frame(frame, known_faces, known_names, marked, tolerance=0.001):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=tolerance)
        name = "Unknown"
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
            if name not in marked:
                mark(name)
                marked.add(name)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return frame

# Function to add a new face
def add_new_face(name, image_file):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(person_dir, exist_ok=True)
    image_path = os.path.join(person_dir, f"{name}.jpg")
    with open(image_path, "wb") as f:
        f.write(image_file.getbuffer())
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        encoding = encodings[0]
        return encoding, name
    return None, None

# Function to capture an image using webcam
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cap.release()
        return frame
    cap.release()
    return None

def main():
    st.set_page_config(page_title="Face Recognition", layout="wide")
    
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #ADD8E6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Face Recognition")
    st.write("Face recognition is the process of identifying a person from an image or video feed.")
    
    # Load known faces
    known_faces, known_names = load_known_faces()
    marked = set()

    # Display an image
    st.image('F:\\project_MCA\\face recog\\Face Recog attandace\\.venv\\FaceRAbgIMG.png', use_column_width=True)

    # Add new face
    st.header("Add New Face")
    name = st.text_input("Name")
    image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if st.button("Add Face") and name and image_file:
        encoding, new_name = add_new_face(name, image_file)
        if encoding is not None and new_name:
            known_faces.append(encoding)
            known_names.append(new_name)
            st.success(f"Added {new_name} successfully!")
        else:
            st.error("Failed to add face. Please try again with a clear image.")
    
    # Capture new face using webcam
    if st.button("Capture Image"):
        captured_image = capture_image()
        if captured_image is not None:
            cv2.imwrite(f'{name}.jpg', captured_image)
            st.image(captured_image, channels="BGR")
            if st.button("Save Captured Face") and name:
                person_dir = os.path.join(KNOWN_FACES_DIR, name)
                os.makedirs(person_dir, exist_ok=True)
                image_path = os.path.join(person_dir, f"{name}.jpg")
                cv2.imwrite(image_path, captured_image)
                encoding, new_name = face_recognition.face_encodings(captured_image)[0], name
                known_faces.append(encoding)
                known_names.append(new_name)
                st.success(f"Added {new_name} successfully!")
        else:
            st.error("Failed to capture image. Please try again.")

    start = st.button("Start Recognition")
    stop_button = st.button("Stop Recognition")

    if start:
        cap = cv2.VideoCapture(0)
        stop = False

        # Stream the video
        frame_placeholder = st.empty()
        while not stop:
            ret, frame = cap.read()
            if not ret:
                st.write("Failed to capture frame.")
                break
            frame = process_frame(frame, known_faces, known_names, marked, tolerance=0.4)  # Adjust tolerance for better accuracy
            frame_placeholder.image(frame, channels="BGR")
            
            if stop_button:
                stop = True
        
        cap.release()
        cv2.destroyAllWindows()

    # Display the attendance data
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        st.subheader("Attendance Records")
        st.dataframe(df)

if __name__ == "__main__":
    main()
