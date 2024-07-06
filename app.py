import cv2
import streamlit as st
from object_detector import *
import numpy as np
import time

st.title("Video Capture with OpenCV")

camera_IP = st.sidebar.text_input("Masuka IP camera Eksternal", "http://192.168.0.100:8080/video")
cap = cv2.VideoCapture(camera_IP)

if st.sidebar.button("Submit"):
    if camera_IP:
        st.write(camera_IP)
    else:
        st.sidebar.write("Masukkan teks terlebih dahulu.")

frame_placeholder = st.empty()

stop_button_pressed = st.button("Stop")

if not cap.isOpened():
    st.error("Error: Could not open video file.")
    exit()

# Load Aruco detector
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
parameters = cv2.aruco.DetectorParameters()

# Load Object Detector
detector = detectorObj()

while cap.isOpened():
    ret, img = cap.read()

    if not ret:
        st.write("End of video file reached.")
        break

    # Check if the frame is empty
    if img is None or img.size == 0:
        st.error("Error: Captured frame is empty.")
        continue

    # Get Aruco marker
    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:
        # Draw polygon around the marker
        int_corners = np.int32(corners)
        cv2.polylines(img, int_corners, True, (0, 255, 0), 5)

        # Aruco Perimeter
        aruco_perimeter = cv2.arcLength(corners[0], True)

        # Pixel to cm ratio
        pixel_cm_ratio = aruco_perimeter / 20  # The ArUco is 5x5 so it's round will be 20 (5+5+5+5)

        contours = detector.detect_objects(img)

        # Draw objects boundaries
        for cnt in contours:
            # Get rect
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect

            # Get Width and Height of the Objects by applying the Ratio pixel to cm
            object_width = w / pixel_cm_ratio
            object_height = h / pixel_cm_ratio

            # Display rectangle
            box = cv2.boxPoints(rect)
            box = np.int32(box)

            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.polylines(img, [box], True, (255, 0, 0), 2)
            cv2.putText(img, f"Width {round(object_width, 1)} cm", (int(x - 100), int(y - 20)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            cv2.putText(img, f"Height {round(object_height, 1)} cm", (int(x - 100), int(y + 15)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)

    # Display the frame in Streamlit
    frame_placeholder.image(img, channels="BGR")

    # Sleep for 0.2 seconds
    time.sleep(0.2)

    # Stop if the stop button is pressed
    if stop_button_pressed:
        break

cap.release()
cv2.destroyAllWindows()
