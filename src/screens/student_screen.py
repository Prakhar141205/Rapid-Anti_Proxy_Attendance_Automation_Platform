import streamlit as st

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.style_base_layout import style_base_layout, style_background_dashboard
from src.screens.home_screen import home_screen
import numpy as np
from PIL import Image  # pillow => PIL

from src.database.db import create_teacher, check_teacher_exists, teacher_login, get_all_students, create_student
from src.pipeline.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipeline.voice_pipeline import get_voice_embeddings


show_registration = False

def student_dashboard():
    st.header("student dashboard")

def student_screen():

    style_background_dashboard()
    style_base_layout()

    if 'student_data' in st.session_state:
        student_dashboard()
        return
    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2 :
        if st.button("Go Back Home", type="secondary", key="loginbackbutton", shortcut="control+backspace"):
            home_screen()

    st.header("Login using FaceID", text_alignment='center')
    st.space()
    st.space()
    
    img_source = st.camera_input("Keep your face at the center")
    if img_source:
        img = np.array(Image.open(img_source))

        with st.spinner("AI is scanning..."):
            detected, all_ids, num_faces = predict_attendance()

            if num_faces == 0:
                st.error("No face found!")
            elif num_faces > 1:
                st.error("Multiple faces found")
            else :
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()

                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        import time
                        time.sleep(1)
                        st.rerun()
                else :
                    st.info("Face not recognized! You might be a new Student")

                    show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header("Register your profile here")
            new_name = st.text_input("Enter your name", placeholder="your name")

            st.subheader("Optional: Voice Enrollment")
            st.info("Enroll for voice only attendance")

            audio_data = None
            try:
                 audio_data = st.audio_input("Record a short Phrase")
            except Exception:
                st.error("audio data failed")

            if st.button("Create Account", type='primary'):
                if new_name:
                    with st.spinner("Creating Profile.."):
                        img  = np.array(Image.open(img_source))
                        encoding = get_face_embeddings(img)
                        if encoding:
                            face_emb = encoding.tolist()[0]

                            voice_emb = None

                        response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = response_data[0]
                            st.toast(f"Profile Created! Hi {student['name']}")
                            import time
                            time.sleep(1)
                            st.rerun()
                
                else:
                    st.error("Your face is not captured properly")
                    
                

            else:
                st.warning("Please Enter your name")


    footer_dashboard()