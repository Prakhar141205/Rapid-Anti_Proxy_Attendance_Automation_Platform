import streamlit as st

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.style_base_layout import style_base_layout, style_background_dashboard
from src.screens.home_screen import home_screen
import numpy as np
from PIL import Image  # pillow => PIL

from src.database.db import create_teacher, check_teacher_exists, teacher_login, enroll_student_to_subject, unenroll_student_to_subject
from src.database.db import get_all_students, create_student, get_student_attendance, get_student_subjects
from src.pipeline.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipeline.voice_pipeline import get_voice_embeddings
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card_component import subject_card

show_registration = False

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2 :
        st.subheader(f"""Welcome {student_data['name']}""")
        if st.button("Logout", type="secondary", key="loginbackbutton", shortcut="control+backspace"):
            st.session_state.is_logged_in = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header("your enrolled subject")
    with c2:
        if st.button("Enroll in subject", type='primary', width='stretch'):
            enroll_dialog()


    st.divider() 

    with st.spinner("Loading your enrolled subject..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    
    stats_map = {}
    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {'Total': 0, 'Attended': 0}
        stats_map[sid]['Total'] += 1

        if logs.get('is_present'):
            stats_map[sid]['Attended'] += 1

    cols = st.columns(2)

    for i, sub_node in  enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(sid, {'Total': 0, 'Attended': 0})
        def unenroll_button():
            if st.button("Unroll from this subject"):
                unenroll_student_to_subject(student_id, sid)
        with cols[i % 2]:
            subject_card(
                name= sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ("", 'Total', stats['Total']),
                    ("", 'Attended', stats['Attended'])

                ],
                footer_callback=unenroll_button()
            )


    footer_dashboard()
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