import cv2
import numpy as np
import sqlite3
import threading
import pyttsx3

DB_FILE = 'videos.db'

def create_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY, path TEXT, tamper_detected INTEGER, scene_change_detected INTEGER)''')
    conn.commit()
    conn.close()

def generate_frames(camera_index, frame_width, frame_height, brightness, tamper_threshold, scene_change_threshold):
    cap = cv2.VideoCapture(camera_index)
    cap.set(3, frame_width)
    cap.set(4, frame_height)
    cap.set(10, brightness)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    engine = pyttsx3.init()

    ret, prev_frame = cap.read()
    if not ret:
        print(f"Unable to read image from camera {camera_index}")
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_hist = cv2.calcHist([prev_gray], [0], None, [256], [0, 256])
    prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tamper_detected = 0
        scene_change_detected = 0

        if is_tampered(frame, tamper_threshold):
            print(f"Camera Tampering Detected on camera {camera_index}")
            tamper_detected = 1
            cv2.putText(frame, "Camera Tampering Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            engine.say("Camera Tampering Detected")
            engine.runAndWait()

        if is_scene_change(prev_hist, frame, scene_change_threshold):
            print(f"Scene Change Detected on camera {camera_index}")
            scene_change_detected = 1
            cv2.putText(frame, "Scene Change Detected", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            engine.say("Scene Change Detected")
            engine.runAndWait()

        video_path = 'path_to_video'

        c.execute("INSERT INTO videos (path, tamper_detected, scene_change_detected) VALUES (?, ?, ?)",
                  (video_path, tamper_detected, scene_change_detected))
        conn.commit()

        prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prev_hist = cv2.calcHist([prev_gray], [0], None, [256], [0, 256])
        prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()

        yield frame

    cap.release()

def is_tampered(frame, threshold=30):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    return mean_brightness < threshold

def is_scene_change(prev_hist, current_frame, threshold=0.7):
    gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
    return correlation < threshold
