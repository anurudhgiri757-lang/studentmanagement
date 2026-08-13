import streamlit as st

from supabase_client import create_parent, list_parents


def render_parents(user: dict) -> None:
    st.title("👨‍👩‍👧 Parent Management")
    with st.form("parent_form"):
        full_name = st.text_input("Full name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        occupation = st.text_input("Occupation")
        emergency_contact = st.text_input("Emergency contact")
        submitted = st.form_submit_button("Save parent")
        if submitted:
            create_parent(full_name=full_name, email=email, phone=phone, occupation=occupation, emergency_contact=emergency_contact)
            st.success("Parent saved successfully")

    st.subheader("Parent records")
    st.dataframe(list_parents(), use_container_width=True, hide_index=True)
