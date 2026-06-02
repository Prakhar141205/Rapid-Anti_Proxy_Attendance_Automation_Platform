import streamlit as st

from src.database.db import enroll_student_to_subject , create_attendance
from src.database.config import supabase
from PIL import Image
import time

@st.dialog("Attendance Reports")

def show_attendance_results(df, log):
   st.write("please review before confirming")
   st.dataframe(df, hidden_index=True, width='stretch')

   c1, c2 = st.columns(2)

   with c1:
      if st.button("Discard", width='stretch'):
         st.session_state.voice_attendance_results = None
         st.rerun()
   
   with c2:
      if st.button("confirm & save", type='primary', width='stretch'):
         try:
            create_attendance(log)
            st.toast("Attendance Taken")
            st.session_state.attendance_images = []
            st.session_state.voice_attendance_results = None
            st.rerun()

         except Exception as e:
            st.error (f"Sync Failed!")

def attendance_result_dialog(df,attendance_log):

      show_attendance_results(df, attendance_log)
   