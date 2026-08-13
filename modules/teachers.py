import streamlit as st

from supabase_client import create_teacher, list_teachers


def render_teachers(user: dict) -> None:
    st.title("🧑‍🏫 Teacher Management")
    with st.form("teacher_form"):
        full_name = st.text_input("Full name")
        employee_id = st.text_input("Employee ID")
        department = st.text_input("Department")
        qualification = st.text_input("Qualification")
        subject = st.text_input("Subject")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        salary = st.number_input("Salary", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Save teacher")
        if submitted:
            create_teacher(
                full_name=full_name,
                employee_id=employee_id,
                department=department,
                qualification=qualification,
                subject=subject,
                email=email,
                phone=phone,
                salary=salary,
            )
            st.success("Teacher saved successfully")

    st.subheader("Teacher records")
    st.dataframe(list_teachers(), use_container_width=True, hide_index=True)
