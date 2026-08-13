import streamlit as st

from supabase_client import create_exam, create_mark, list_exams, list_marks, list_students


def render_exams(user: dict) -> None:
    st.title("📝 Exams & Results")
    with st.expander("Create exam"):
        with st.form("exam_form"):
            name = st.text_input("Exam name")
            subject = st.text_input("Subject")
            schedule = st.text_input("Schedule")
            hall = st.text_input("Hall")
            submitted = st.form_submit_button("Save exam")
            if submitted:
                create_exam(name=name, subject=subject, schedule=schedule, hall=hall)
                st.success("Exam created")

    with st.expander("Enter marks"):
        students = list_students()
        if not students:
            st.info("No students available")
            return
        student_lookup = {item["student_id"]: item["full_name"] for item in students}
        student_id = st.selectbox("Student", list(student_lookup.keys()), format_func=lambda value: student_lookup[value])
        subject = st.text_input("Subject", key="mark_subject")
        marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=1.0)
        if st.button("Save marks"):
            create_mark(student_id=student_id, subject=subject, marks=marks)
            st.success("Marks saved")

    st.subheader("Exam schedule")
    st.dataframe(list_exams(), use_container_width=True, hide_index=True)
    st.subheader("Marks")
    st.dataframe(list_marks(), use_container_width=True, hide_index=True)
