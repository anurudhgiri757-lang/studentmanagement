import streamlit as st
import time

from modules.dashboard import render_dashboard
from modules.students import render_students
from modules.teachers import render_teachers
from modules.parents import render_parents
from modules.classes import render_classes
from modules.attendance import render_attendance
from modules.exams import render_exams
from modules.fees import render_fees
from modules.timetable import render_timetable
from modules.announcements import render_announcements
from modules.reports import render_reports
from modules.library import render_library
from modules.transport import render_transport
from modules.inventory import render_inventory
from modules.settings import render_settings
from supabase_client import authenticate_user, get_user_by_email, register_user, search_records
from utils.helpers import PAGE_ICONS, ROLE_LABELS, ROLE_ICONS, format_page_with_icon, get_accessible_pages
from utils.validators import validate_email, validate_password, validate_phone

st.set_page_config(page_title="Smart School Management System", page_icon="🏫", layout="wide")


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        .stApp { background: linear-gradient(135deg, #f7fbff 0%, #eef6ff 100%); }
        .block-container { padding-top: 1.25rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
        .stTabs [data-baseweb="tab"] { border-radius: 999px; padding: 0.4rem 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_session() -> None:
    defaults = {
        "authenticated": False,
        "user": None,
        "last_activity": time.time(),
        "theme": "light",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _logout() -> None:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.last_activity = time.time()


def _check_inactivity() -> None:
    if st.session_state.authenticated and time.time() - st.session_state.last_activity > 1800:
        _logout()
        st.warning("You were logged out due to inactivity.")
        st.rerun()


def _auth_screen() -> None:
    st.title("🏫 Smart School Management System")
    st.caption("Secure, modern school administration for students, staff, parents, and administrators.")

    auth_tab, register_tab = st.tabs(["Login", "Register"])

    with auth_tab:
        st.subheader("Welcome back")
        email = st.text_input("Email or Username", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        remember_me = st.checkbox("Remember me")
        if st.button("Login", key="login_submit"):
            if not email or not password:
                st.error("Both fields are required.")
            else:
                user = authenticate_user(email, password)
                if user is None:
                    st.error("Invalid credentials. Please try again.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.last_activity = time.time()
                    if remember_me:
                        st.session_state.theme = "light"
                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()

    with register_tab:
        st.subheader("Create an account")
        full_name = st.text_input("Full Name", key="reg_full_name")
        username = st.text_input("Username", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        phone = st.text_input("Phone Number", key="reg_phone")
        password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        role = st.selectbox("Role", list(ROLE_LABELS.keys()), format_func=lambda value: ROLE_LABELS[value], key="reg_role")
        if st.button("Create account", key="register_submit"):
            if not full_name or not username or not email or not phone or not password or not confirm_password:
                st.error("All fields are required.")
                return
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return
            if not validate_phone(phone):
                st.error("Please enter a valid phone number.")
                return
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            valid, reason = validate_password(password)
            if not valid:
                st.error(reason)
                return
            if get_user_by_email(email):
                st.error("An account with this email already exists.")
                return
            if any(item.get("username") == username for item in search_records(username) if item.get("type") == "user"):
                st.error("That username is already taken.")
                return
            user = register_user(
                full_name=full_name,
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
            )
            st.success(f"Account created successfully for {user['full_name']}.")
            st.info("You can now sign in with your new credentials.")


def _render_sidebar(user: dict) -> None:
    st.sidebar.title("🏫 Smart School")
    st.sidebar.caption(f"{ROLE_ICONS[user['role']]} {ROLE_LABELS[user['role']]}")
    pages = get_accessible_pages(user["role"])
    page_labels = [format_page_with_icon(page) for page in pages]
    selected_label = st.sidebar.radio("Navigation", page_labels, key="page_selection")
    # Map the selected label back to the page name
    page = next((page for page in pages if format_page_with_icon(page) == selected_label), selected_label)
    st.sidebar.divider()
    search_query = st.sidebar.text_input("Global search", placeholder="Search students, teachers, classes...")
    if search_query:
        results = search_records(search_query)
        st.sidebar.caption(f"{len(results)} match(es)")
        for result in results[:5]:
            st.sidebar.write(f"- {result['label']}")
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        _logout()
        st.rerun()
    return page


def main() -> None:
    _init_session()
    _apply_styles()
    _check_inactivity()

    if not st.session_state.authenticated or st.session_state.user is None:
        _auth_screen()
        return

    user = st.session_state.user
    st.session_state.last_activity = time.time()
    page = _render_sidebar(user)

    if page == "Dashboard":
        render_dashboard(user)
    elif page == "Students":
        render_students(user)
    elif page == "Teachers":
        render_teachers(user)
    elif page == "Parents":
        render_parents(user)
    elif page == "Classes":
        render_classes(user)
    elif page == "Attendance":
        render_attendance(user)
    elif page == "Exams":
        render_exams(user)
    elif page == "Fees":
        render_fees(user)
    elif page == "Timetable":
        render_timetable(user)
    elif page == "Announcements":
        render_announcements(user)
    elif page == "Reports":
        render_reports(user)
    elif page == "Library":
        render_library(user)
    elif page == "Transport":
        render_transport(user)
    elif page == "Inventory":
        render_inventory(user)
    elif page == "Settings":
        render_settings(user)


if __name__ == "__main__":
    main()
