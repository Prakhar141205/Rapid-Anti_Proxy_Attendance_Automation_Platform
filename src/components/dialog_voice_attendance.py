import streamlit as st
from src.pipeline.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_results import show_attendance_results

@st.dialog("voice Attendance")

def voice_attendance_dialog(selected_subject_id):
    st.write("Record Audio for voice Attendance")

    audio_data = None
    audio_data = st.audio_input("Record classroom audio")

    if st.button("Analyze audio", width="content", type='primary'):
        with st.spinner("Processing Audio data"):
            enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No students in this course")
                return
            
            candidate_dic = {
                s['students']['student_id']:s['students']['student_id']
                for s in enrolled_students if s['students'].get('voice_embedding')
            }
                
            if candidate_dic:
                st.warning("No enrolled students have voice profile registered")
                return 
            
            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes=audio_bytes, candidate_dict=candidate_dic)
            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                    student = node['students']
                    score = detected_scores.get(int(student['student_id']), [])
                    is_present = len(score) > 0

                    results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": score if is_present else "-",
                            "Status": "Present" if is_present else "Absent"
                        })

                    attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })
                    
            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, log = st.session_state.voice_attendance_results
        show_attendance_results(df_results, log)




