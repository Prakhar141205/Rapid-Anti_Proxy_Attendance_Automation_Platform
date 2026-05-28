import streamlit as st
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.style_base_layout import style_base_layout, style_background_dashboard
from src.screens.home_screen import home_screen



def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    
    if 'teacher_login_type' not in st.session_state or st.session_state['teacher_login_type'] == 'login':

        teacher_screen_login()

    elif st.session_state['teacher_login_type'] == 'register':
        teacher_screen_register()


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
        st.button("Login", icon=":material/passkey:", width='stretch', shortcut="control+enter")
    with bcol2:
        if st.button("Go Back Home", type="secondary", key="loginbackbutton", shortcut="control+backspace"):
            st.session_state['teacher_login_type'] == 'register'
            st.rerun()

    footer_dashboard()



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