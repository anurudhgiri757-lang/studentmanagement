import streamlit as st

from supabase_client import export_backup, import_backup


def render_settings(user: dict) -> None:
    st.title("⚙️ Settings")
    st.subheader("Profile")
    st.write(f"Name: {user['full_name']}")
    st.write(f"Role: {user['role']}")
    st.write(f"Email: {user['email']}")

    st.subheader("Backup and restore")
    backup_path = st.text_input("Backup file path", value="./exports/settings_backup.json")
    if st.button("Export backup"):
        export_backup(backup_path)
        st.success(f"Backup exported to {backup_path}")
    uploaded_file = st.file_uploader("Restore data", type="json")
    if uploaded_file is not None:
        with open("./exports/settings_restore.json", "wb") as handle:
            handle.write(uploaded_file.getvalue())
        import_backup("./exports/settings_restore.json")
        st.success("Data restored successfully")
