import streamlit as st

from supabase_client import create_announcement, list_announcements


def render_announcements(user: dict) -> None:
    st.title("📣 Announcements")
    with st.form("announcement_form"):
        title = st.text_input("Title")
        body = st.text_area("Message")
        audience = st.selectbox("Audience", ["All", "Teachers", "Students", "Parents"])
        submitted = st.form_submit_button("Publish")
        if submitted:
            create_announcement(title=title, body=body, audience=audience)
            st.success("Announcement published")

    st.subheader("Published announcements")
    st.dataframe(list_announcements(), use_container_width=True, hide_index=True)
