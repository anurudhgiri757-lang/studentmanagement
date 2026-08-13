import streamlit as st

from supabase_client import create_class, list_classes


def render_classes(user: dict) -> None:
    st.title("🏫 Class Management")
    with st.form("class_form"):
        name = st.text_input("Class name")
        teacher = st.text_input("Assigned teacher")
        subjects = st.text_input("Subjects")
        section = st.text_input("Section")
        room_number = st.text_input("Room number")
        capacity = st.number_input("Capacity", min_value=1, step=1)
        submitted = st.form_submit_button("Save class")
        if submitted:
            create_class(name=name, teacher=teacher, subjects=subjects, section=section, room_number=room_number, capacity=int(capacity))
            st.success("Class saved successfully")

    st.subheader("Class records")
    st.dataframe(list_classes(), use_container_width=True, hide_index=True)
