import streamlit as st

from supabase_client import create_library_book, list_library_books


def render_library(user: dict) -> None:
    st.title("📚 Library")
    with st.form("library_form"):
        title = st.text_input("Book title")
        author = st.text_input("Author")
        category = st.text_input("Category")
        copies = st.number_input("Copies", min_value=1, step=1)
        submitted = st.form_submit_button("Save book")
        if submitted:
            create_library_book(title=title, author=author, category=category, copies=int(copies))
            st.success("Book saved")

    st.subheader("Library catalog")
    st.dataframe(list_library_books(), use_container_width=True, hide_index=True)
