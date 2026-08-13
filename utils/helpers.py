from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

ROLE_LABELS = {
    "admin": "Administrator",
    "teacher": "Teacher",
    "student": "Student",
    "parent": "Parent",
}

ROLE_ICONS = {
    "admin": "👑",
    "teacher": "🧑‍🏫",
    "student": "🎓",
    "parent": "👨‍👩‍👧",
}

PAGE_ICONS = {
    "Dashboard": "📊",
    "Students": "🎓",
    "Teachers": "🧑‍🏫",
    "Parents": "👨‍👩‍👧",
    "Classes": "🏫",
    "Attendance": "📝",
    "Exams": "🧾",
    "Fees": "💰",
    "Timetable": "📅",
    "Announcements": "📣",
    "Reports": "📁",
    "Library": "📚",
    "Transport": "🚌",
    "Inventory": "📦",
    "Settings": "⚙️",
}


def format_currency(amount: float | int) -> str:
    return f"${amount:,.2f}"


def get_accessible_pages(role: str) -> List[str]:
    pages = ["Dashboard"]
    if role == "admin":
        return ["Dashboard", "Students", "Teachers", "Parents", "Classes", "Attendance", "Exams", "Fees", "Timetable", "Announcements", "Reports", "Library", "Transport", "Inventory", "Settings"]
    if role == "teacher":
        return ["Dashboard", "Students", "Attendance", "Exams", "Fees", "Announcements", "Reports"]
    if role == "student":
        return ["Dashboard", "Attendance", "Fees", "Announcements", "Reports"]
    return ["Dashboard", "Attendance", "Fees", "Announcements"]


def format_page_with_icon(page: str) -> str:
    icon = PAGE_ICONS.get(page, "")
    return f"{icon} {page}" if icon else page


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def summarize_records(records: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in records:
        value = item.get(key, "Unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts
