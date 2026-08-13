import streamlit as st

from supabase_client import export_backup, import_backup
from utils.pdf_generator import export_simple_pdf


def render_reports(user: dict) -> None:
    st.title("📄 Reports")
    st.subheader("Export PDF")
    if st.button("Generate sample PDF"):
        path = export_simple_pdf("./exports/school_report.pdf", ["Smart School Management System", "Student summary exported successfully."])
        st.success(f"PDF generated at {path}")

    st.subheader("Backup")
    backup_path = st.text_input("Backup file path", value="./exports/backup.json")
    if st.button("Export backup"):
        export_backup(backup_path)
        st.success(f"Backup created at {backup_path}")

    uploaded_file = st.file_uploader("Restore backup", type="json")
    if uploaded_file is not None:
        with open("./exports/uploaded_backup.json", "wb") as handle:
            handle.write(uploaded_file.getvalue())
        import_backup("./exports/uploaded_backup.json")
        st.success("Backup restored")
