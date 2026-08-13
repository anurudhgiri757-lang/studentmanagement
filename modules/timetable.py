import streamlit as st

from supabase_client import (
    create_timetable_entry,
    list_timetable,
)


def render_timetable(user: dict) -> None:
    st.title("🗓️ Timetable")

    with st.form("timetable_form"):
        day = st.text_input("Day")
        period = st.text_input("Period")
        subject = st.text_input("Subject")
        teacher = st.text_input("Teacher")
        room = st.text_input("Room")

        submitted = st.form_submit_button(
            "Save timetable entry"
        )

        if submitted:

            if not day.strip():
                st.error("Day is required.")
                return

            if not subject.strip():
                st.error("Subject is required.")
                return

            try:
                create_timetable_entry(
                    day=day.strip(),
                    period=period.strip(),
                    subject=subject.strip(),
                    teacher=teacher.strip(),
                    room=room.strip(),
                )

                st.success(
                    "Timetable entry saved successfully!"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "Failed to save timetable entry to Supabase."
                )
                st.code(str(e))

    st.subheader("Timetable")

    try:
        timetable = list_timetable()

        if timetable:
            st.dataframe(
                timetable,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No timetable entries found.")

    except Exception as e:
        st.error(
            "Could not load timetable from Supabase."
        )
        st.code(str(e))
