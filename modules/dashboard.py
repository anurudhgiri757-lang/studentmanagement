import streamlit as st
import pandas as pd
import plotly.express as px

from supabase_client import get_dashboard_snapshot, list_announcements, list_attendance, list_exams, list_fees, list_students, list_teachers
from utils.helpers import format_currency


def render_dashboard(user: dict) -> None:
    st.title("📊 Dashboard")
    snapshot = get_dashboard_snapshot()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Students", snapshot["students"])
    col2.metric("Teachers", snapshot["teachers"])
    col3.metric("Parents", len(list_students()) if False else 0)
    col4.metric("Classes", snapshot["classes"])

    st.subheader("School overview")
    overview = pd.DataFrame(
        [
            {"Metric": "Attendance records", "Value": snapshot["attendance"]},
            {"Metric": "Fee collection", "Value": format_currency(snapshot["fees"])},
            {"Metric": "Exams", "Value": snapshot["exams"]},
            {"Metric": "Announcements", "Value": snapshot["announcements"]},
        ]
    )
    st.dataframe(overview, hide_index=True)

    chart_df = pd.DataFrame(
        {
            "Category": ["Students", "Teachers", "Classes", "Exams"],
            "Count": [snapshot["students"], snapshot["teachers"], snapshot["classes"], snapshot["exams"]],
        }
    )
    fig = px.bar(chart_df, x="Category", y="Count", color="Category", title="Institution Snapshot")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Announcements")
    for announcement in list_announcements()[:5]:
        with st.expander(announcement.get("title", "Announcement")):
            st.write(announcement.get("body", ""))
