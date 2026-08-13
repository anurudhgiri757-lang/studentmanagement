# Smart School Management System

A polished Streamlit application for managing students, teachers, parents, classes, attendance, exams, fees, library items, transport, and inventory. The app uses a local JSON-backed store by default so it runs immediately, while remaining compatible with Supabase-backed deployment.

## Features

- Secure registration and login with role-based access control
- Admin, teacher, student, and parent perspectives
- Dashboard with KPIs, charts, and announcements
- Student, teacher, parent, class, and attendance management
- Exams, grades, fee tracking, timetable, library, transport, inventory, and reports
- PDF report export and backup/restore support

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run app.py
```

3. To connect to Supabase, update the values in `.env` with your project URL and anon/service role key.

## File structure

- `app.py` main Streamlit entry point
- `supabase_client.py` data access layer with local persistence and optional Supabase-ready helpers
- `modules/` feature modules for each management area
- `utils/` shared helpers, validators, and PDF generator
- `supabase_schema.sql` production-ready PostgreSQL schema example

## Notes

- The application is fully functional out of the box using the local JSON store.
- Replace the `.env` values with your real Supabase credentials when you want remote persistence and authentication.
