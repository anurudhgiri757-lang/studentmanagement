import streamlit as st

from supabase_client import create_student, list_students


def render_students(user: dict) -> None:
    st.title("🎓 Student Management")
    st.subheader("Add student")
    with st.form("student_form"):
        full_name = st.text_input("Full name")
        student_id = st.text_input("Student ID")
        grade_level = st.text_input("Grade level")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        guardian_name = st.text_input("Guardian name")
        address = st.text_area("Address")
        medical_info = st.text_area("Medical information")
        submitted = st.form_submit_button("Save student")
        if submitted:
            create_student(
                full_name=full_name,
                student_id=student_id,
                grade_level=grade_level,
                email=email,
                phone=phone,
                guardian_name=guardian_name,
                address=address,
                medical_info=medical_info,
            )
            st.success("Student saved successfully")

    st.subheader("Student records")
    students = list_students()
    st.dataframe(students, use_container_width=True, hide_index=True)
