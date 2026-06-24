import streamlit as st
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.style_base_layout import style_base_layout, style_background_dashboard
from src.screens.home_screen import home_screen

from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photos import add_photos_dialog

from src.database.db import create_teacher, check_teacher_exists, teacher_login, get_teacher_subjects, get_attendance_for_teacher
from src.components.dialog_create_subject import create_Subject_dialog
from src.components.subject_card_component import subject_card
from src.pipeline.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
import numpy as np
import pandas as pd
from src.database.config import supabase
from datetime import datetime




def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    
    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state['teacher_login_type'] == 'login':

        teacher_screen_login()

    elif st.session_state['teacher_login_type'] == 'register':
        teacher_screen_register()

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2 :
        st.subheader(f"""Welcome {teacher_data['name']}""")
        if st.button("Logout", type="secondary", key="loginbackbutton", shortcut="control+backspace"):
            st.session_state.is_logged_in = False
            del st.session_state.teacher_data
            st.rerun()


    st.space()

    if 'current_teacher_tab' not in  st.session_state:
        st['current_teacher_tab'] = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = 'primary' if st.session_state.current_teacher_tab == 'take_attendance' else 'tertiary'
        st.button('Take Attendace', icon=':material/ar_on_you:', width='stretch', type=type1)
        st.session_state.current_teacher_tab = 'take_attendance'
        st.rerun()

    with tab2:
        type2 = 'primary' if st.session_state.current_teacher_tab == 'manage_subjects' else 'tertiary'

        st.button('Manage Subjects', icon=':material/book_ribbon:', width='stretch', type=type2)
        st.session_state.current_teacher_tab = 'manage_subjects'
        st.rerun()

    with tab3:
        type3 = 'primary' if st.session_state.current_teacher_tab == 'attendance_records' else 'tertiary'

        st.button('Attendace Records', icon=':material/cards_stack:', width='stretch', type=type3)
        st.session_state.current_teacher_tab = 'attendance_records'
        st.rerun()

    if st.session_state.current_teacher_tab == 'take_attendance':
        teacher_tab_take_attendance()

    if st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == 'attendance_records':
        teacher_tab_attendance_records()

    st.divider()
    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header("Take Attendance")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []
    
    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("You haven't created any subject yet! Please create one to begin")
        return
    
    subject_options = {f"{s['name']}-{s['subject_code']}" : s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox("Select subjects" , options=list(subject_options.keys()))

    with col2:
        if st.button("Add photos", type='primary', icon=":material/photo_prints:", width='stretch'):
            add_photos_dialog()

        
        selected_subject_id = subject_options[selected_subject_label]
    
    st.divider()
            
    if st.session_state.attendance_images:
        st.header("Added photos")
        gallery_cols = st.columns(4)

        for idx, img in st.session_state.attendance_images:
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    
    has_photos = bool(st.session_state.attendance_images)

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Clear All photos", width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button("Run Face Analysis", type='secondary', width='stretch' , icon=':material/analytics:', disabled= not has_photos):
            with st.spinner("Deep scanning the photos"):
                all_detected_ids = {}

                for idx, img in st.session_state.attendance_images:
                    image_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(image_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo: {idx + 1}")
                enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning("No students in this course")
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "Present" if is_present else "Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results),attendance_to_log)

    with c3:
        if st.button("use Voice Assistant", type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)

def teacher_tab_manage_subjects():
    # st.header("Manage Subjects")

    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)

    with col1:
        st.header("Manage Subjects", width='stretch')
    with col2:
        if st.button("Create New Subjects", width='stretch'):
            create_Subject_dialog(teacher_id)

    ## list all the subjects

    subjects = get_teacher_subjects(teacher_id)

    if subjects:
        for sub in subjects:

            stats = [
                (" ", "Students", sub['total_students']),
                (" ", "Classes", sub['total_classes'])
            ]

        def share_btn():
            if st.button(f"Share code: {sub['name']}", key = f"share_{sub['subject_code']}", icon=":material/share:"):
                share_subject_dialog(sub['name'], sub['subject_code'])

            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats = stats,
            footer_callback = share_btn
        )
    else:
        st.info("No subject found! create one")
def teacher_tab_attendance_records():
    st.header("Attendance Records")

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return 
    
    data = []

    for r in records:
        timestamp = r.get('timestamp')

        data.append({
            'ts_group': timestamp.split(".")[0] if timestamp else None,
            'Time': datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %I-%M-%p") if timestamp else "N/A",
            'Subject': r['subjects']['name'],
            'Subject code': r['subjects']['subject_code'],
            'is_present': bool(r.get('is_present', False))

         })
    
    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject code']).agg(
            Present_count = ('is_present', 'sum'),
            Total_count = ('is_present', 'count')
        ).reset_index()
    )
    
    summary['Attendance Stats'] = (
        "  " + summary['Present_count'].astype(str) + " /" + 
        summary['Total_count'].astype(str) + 'Students'
    )

    display_df = (summary.sort_values(by='ts_group', ascending=False),
                  [['Time', 'Subject', 'Subject code', 'Attendance Stats']]
                  )
    
    st.dataframe(display_df, width='stretch', hide_index=True)


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True

        return True
    else :
        return False

def teacher_screen_login():

    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2 :
        if st.button("Go Back Home", type="secondary", key="loginbackbutton", shortcut="control+backspace"):
            home_screen()

    st.header("Login using password", text_alignment='center')

    st.space()
    st.space()

    teacher_username = st.text_input("Enter username ",placeholder='your username')

    teacher_name = st.text_input("Enter your name ",placeholder='your name')
    teacher_pass = st.text_input("Enter password ", type='password', placeholder='your password')

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder='your password')

    st.divider()
    bcol1, bcol2  = st.columns(2)

    with bcol1:
        if st.button("Login", icon=":material/passkey:", width='stretch', shortcut="control+enter"):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome Back")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password")
    with bcol2:
        if st.button("Register Instead", type="secondary", key="loginback", shortcut="control+backspace"):
            st.session_state['teacher_login_type'] = 'register'
            st.rerun()

    footer_dashboard()

def  register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_name or not teacher_pass or not teacher_username:
        return False , "All Fields are required"
    
    if check_teacher_exists(teacher_username):
        return False, "username already taken"
    
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't Match"
    
    try:
        create_teacher(teacher_name, teacher_pass, teacher_username)
        return True, "Successfully Created! Login Now!"
    except Exception as e:
        return False, "Unexpected Error"


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()