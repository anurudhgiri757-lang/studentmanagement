import streamlit as st

from supabase_client import create_attendance_record, list_attendance, list_students


def render_attendance(user: dict) -> None:
    st.title("📅 Attendance")
    students = list_students()
    if not students:
        st.info("Add students before creating attendance entries.")
        return

    student_names = {item["student_id"]: item["full_name"] for item in students}
    student_id = st.selectbox("Student", list(student_names.keys()), format_func=lambda value: student_names[value])
    attendance_date = st.date_input("Date")
    status = st.selectbox("Status", ["Present", "Absent", "Late", "Leave"])
    if st.button("Save attendance"):
        create_attendance_record(student_id=student_id, date=str(attendance_date), status=status)
        st.success("Attendance recorded")

    st.subheader("Attendance records")
    st.dataframe(list_attendance(), use_container_width=True, hide_index=True)
