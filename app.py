import streamlit as st
import core
import cv2
from PIL import Image

core.create_db()

st.title('Camera Monitoring System')

camera_index = st.sidebar.number_input('Camera Index', value=0)
frame_width = st.sidebar.number_input('Frame Width', value=640)
frame_height = st.sidebar.number_input('Frame Height', value=480)
brightness = st.sidebar.number_input('Brightness', value=100)
tamper_threshold = st.sidebar.number_input('Tamper Threshold', value=30)
scene_change_threshold = st.sidebar.number_input('Scene Change Threshold', value=0.7)

if st.button('Start Detection'):
    stframe = st.empty()

    for frame in core.generate_frames(camera_index, frame_width, frame_height, brightness, tamper_threshold,
                                      scene_change_threshold):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        stframe.image(frame_rgb, channels="RGB")
    st.write('Detection completed. **Thank You.**')
