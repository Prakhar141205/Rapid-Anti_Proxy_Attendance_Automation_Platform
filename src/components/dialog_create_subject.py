import streamlit as st

from src.database.db import create_subject


@st.dialog("Create New Subject")
def create_Subject_dialog(teacher_id):
    st.write("Enter the details of the New subject")

    sub_id = st.text_input("Enter the id of the subject.", placeholder='CS101')
    sub_name = st.text_input("Enter the subject name", placeholder='Ex. English')
    sub_section = st.text_input("Enter the subject section", placeholder="Ex. A")


    if st.button("Create subject now!", type='primary', width='stretch'):

        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject Created Successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

        else :
            st.warning("All the fields are required!")


