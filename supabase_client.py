import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse
import socket

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

from config import get_data_dir, get_db_path

project_root = Path(__file__).resolve().parent
dotenv_path = project_root / ".env"

if load_dotenv:
    load_dotenv(dotenv_path=dotenv_path)
elif dotenv_path.exists():
    with dotenv_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
# Optional stronger service role key to use for server-side operations
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE", "")


def _supabase_insert(table: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Insert a record into Supabase REST endpoint and return the inserted row.
    Raises on failure so callers see Supabase errors instead of silently
    falling back to the local JSON store.
    """
    if not SUPABASE_URL or (not SUPABASE_KEY and not SUPABASE_SERVICE_ROLE):
        raise RuntimeError("SUPABASE_URL or SUPABASE_KEY (or SUPABASE_SERVICE_ROLE) not configured")

    # prefer a server-side service role key when available for inserts
    used_key = SUPABASE_SERVICE_ROLE or SUPABASE_KEY

    # quick DNS resolution check for clearer failures
    try:
        parsed = urllib.parse.urlparse(SUPABASE_URL)
        host = parsed.hostname
        if host:
            socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise RuntimeError(f"DNS resolution failed for Supabase host '{host}': {e}")
    except Exception:
        # non-fatal — continue and let the underlying request report issues
        pass

    url = SUPABASE_URL.rstrip("/") + f"/rest/v1/{table}"
    headers = {
        "apikey": used_key,
        "Authorization": f"Bearer {used_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    body = json.dumps(payload)

    # Prefer requests when available for clearer error handling
    try:
        import requests

        resp = requests.post(url, headers=headers, data=body, timeout=10)
        try:
            resp.raise_for_status()
        except Exception as exc:
            # try to include response body in the error
            content = None
            try:
                content = resp.text
            except Exception:
                content = None
            raise RuntimeError(f"Supabase insert failed: {exc} - {content}")

        data = resp.json()
        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict):
            return data
        return None
    except Exception as req_exc:
        # fallback to urllib if requests is not available or fails
        req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as fh:
                resp_body = fh.read().decode("utf-8")
                parsed = json.loads(resp_body)
                if isinstance(parsed, list) and parsed:
                    return parsed[0]
                if isinstance(parsed, dict):
                    return parsed
                return None
        except urllib.error.HTTPError as he:
            try:
                err_body = he.read().decode("utf-8")
            except Exception:
                err_body = None
            raise RuntimeError(f"Supabase insert HTTPError: {he} - {err_body}")
        except Exception as exc:
            # include original requests exception if present
            raise RuntimeError(f"Supabase insert failed: {exc} (requests error: {req_exc})")


def _default_store() -> Dict[str, Any]:
    return {
        "users": [],
        "students": [],
        "teachers": [],
        "parents": [],
        "classes": [],
        "modules": [],
        "attendance": [],
        "exams": [],
        "marks": [],
        "fees": [],
        "payments": [],
        "timetable": [],
        "announcements": [],
        "library_books": [],
        "issued_books": [],
        "transport": [],
        "vehicles": [],
        "inventory": [],
        "notifications": [],
        "audit_logs": [],
    }


def _ensure_storage() -> None:
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = get_db_path()
    if not db_path.exists():
        with db_path.open("w", encoding="utf-8") as handle:
            json.dump(_default_store(), handle, indent=2)


def _read_store() -> Dict[str, Any]:
    _ensure_storage()
    with get_db_path().open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    for key, value in _default_store().items():
        data.setdefault(key, value)
    return data


def _write_store(data: Dict[str, Any]) -> None:
    _ensure_storage()
    with get_db_path().open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _supabase_get(table: str) -> List[Dict[str, Any]]:
    """Fetch rows from a Supabase table using the REST API.

    Raises on failure so callers can surface Supabase errors.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL or SUPABASE_KEY not configured")

    url = SUPABASE_URL.rstrip("/") + f"/rest/v1/{table}?select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Accept": "application/json",
    }

    try:
        import requests

        resp = requests.get(url, headers=headers, timeout=10)
        try:
            resp.raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"Supabase get failed: {exc} - {resp.text}")
        data = resp.json()
        if isinstance(data, list):
            return data
        return []
    except Exception:
        # fallback to urllib
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as fh:
                resp_body = fh.read().decode("utf-8")
                parsed = json.loads(resp_body)
                if isinstance(parsed, list):
                    return parsed
                return []
        except urllib.error.HTTPError as he:
            try:
                err_body = he.read().decode("utf-8")
            except Exception:
                err_body = None
            raise RuntimeError(f"Supabase get HTTPError: {he} - {err_body}")
        except Exception as exc:
            raise RuntimeError(f"Supabase get failed: {exc}")


def _hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), b"smart-school", 100_000).hex()


def _verify_password(password: str, password_hash: str) -> bool:
    return _hash_password(password) == password_hash


def _append_audit(action: str, detail: str, user_id: Optional[str] = None) -> None:
    data = _read_store()
    data["audit_logs"].append(
        {
            "id": str(uuid.uuid4()),
            "action": action,
            "detail": detail,
            "user_id": user_id,
            "created_at": _now(),
        }
    )
    _write_store(data)


def register_user(full_name: str, username: str, email: str, password: str, phone: str, role: str = "student") -> Dict[str, Any]:
    data = _read_store()
    if any(item.get("email") == email for item in data["users"]):
        raise ValueError("Email already registered")
    if any(item.get("username") == username for item in data["users"]):
        raise ValueError("Username already registered")
    user = {
        "id": str(uuid.uuid4()),
        "full_name": full_name,
        "username": username,
        "email": email,
        "phone": phone,
        "role": role,
        "password_hash": _hash_password(password),
        "created_at": _now(),
    }
    # attempt to persist to Supabase (omit password hash), but always keep local copy for compatibility
    supa_row = None
    try:
        supa_row = _supabase_insert("users", {k: v for k, v in user.items() if k != "password_hash"})
    except Exception:
        supa_row = None

    data["users"].append(user)
    _write_store(data)
    _append_audit("register_user", f"Registered {email}", user_id=user["id"])
    return supa_row or user


def authenticate_user(login_value: str, password: str) -> Optional[Dict[str, Any]]:
    data = _read_store()
    user = next((item for item in data["users"] if item.get("email") == login_value or item.get("username") == login_value), None)
    if user and _verify_password(password, user.get("password_hash", "")):
        return user
    return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    data = _read_store()
    return next((item for item in data["users"] if item.get("email") == email), None)


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    data = _read_store()
    return next((item for item in data["users"] if item.get("id") == user_id), None)


def list_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
    data = _read_store()
    users = data["users"]
    if role:
        users = [item for item in users if item.get("role") == role]
    return users


def sign_up(email: str, password: str, full_name: str, role: str = "student", student_class: Optional[str] = None):
    user = register_user(full_name=full_name, username=email.split("@", 1)[0], email=email, password=password, phone="", role=role)
    return True, user


def sign_in(email: str, password: str):
    user = authenticate_user(email, password)
    if user:
        return True, user
    return False, "Invalid credentials"


def create_student(full_name: str, student_id: str, grade_level: str, email: str, phone: str, guardian_name: str, address: str, medical_info: str) -> Dict[str, Any]:
    data = _read_store()
    student = {
        "id": str(uuid.uuid4()),
        "full_name": full_name,
        "student_id": student_id,
        "grade_level": grade_level,
        "email": email,
        "phone": phone,
        "guardian_name": guardian_name,
        "address": address,
        "medical_info": medical_info,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("students", student)
    except Exception:
        supa_row = None

    data["students"].append(student)
    _write_store(data)
    _append_audit("create_student", f"Created student {student_id}")
    return supa_row or student


def list_students() -> List[Dict[str, Any]]:
    return _read_store()["students"]


def create_teacher(full_name: str, employee_id: str, department: str, qualification: str, subject: str, email: str, phone: str, salary: float) -> Dict[str, Any]:
    data = _read_store()
    teacher = {
        "id": str(uuid.uuid4()),
        "full_name": full_name,
        "employee_id": employee_id,
        "department": department,
        "qualification": qualification,
        "subject": subject,
        "email": email,
        "phone": phone,
        "salary": salary,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("teachers", teacher)
    except Exception:
        supa_row = None

    data["teachers"].append(teacher)
    _write_store(data)
    _append_audit("create_teacher", f"Created teacher {employee_id}")
    return supa_row or teacher


def list_teachers() -> List[Dict[str, Any]]:
    return _read_store()["teachers"]


def create_parent(full_name: str, email: str, phone: str, occupation: str, emergency_contact: str) -> Dict[str, Any]:
    data = _read_store()
    parent = {
        "id": str(uuid.uuid4()),
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "occupation": occupation,
        "emergency_contact": emergency_contact,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("parents", parent)
    except Exception:
        supa_row = None

    data["parents"].append(parent)
    _write_store(data)
    _append_audit("create_parent", f"Created parent {full_name}")
    return supa_row or parent


def list_parents() -> List[Dict[str, Any]]:
    return _read_store()["parents"]


def create_class(name: str, teacher: str, subjects: str, section: str, room_number: str, capacity: int) -> Dict[str, Any]:
    data = _read_store()
    school_class = {
        "id": str(uuid.uuid4()),
        "name": name,
        "teacher": teacher,
        "subjects": subjects,
        "section": section,
        "room_number": room_number,
        "capacity": capacity,
        "created_at": _now(),
    }
    data["classes"].append(school_class)
    _write_store(data)
    return school_class


def list_classes() -> List[Dict[str, Any]]:
    return _read_store()["classes"]


def create_attendance_record(student_id: str, date: str, status: str) -> Dict[str, Any]:
    data = _read_store()
    record = {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "date": date,
        "status": status,
        "created_at": _now(),
    }
    data["attendance"].append(record)
    _write_store(data)
    return record


def list_attendance() -> List[Dict[str, Any]]:
    return _read_store()["attendance"]


def create_exam(name: str, subject: str, schedule: str, hall: str) -> Dict[str, Any]:
    data = _read_store()
    exam = {
        "id": str(uuid.uuid4()),
        "name": name,
        "subject": subject,
        "schedule": schedule,
        "hall": hall,
        "created_at": _now(),
    }
    data["exams"].append(exam)
    _write_store(data)
    return exam


def list_exams() -> List[Dict[str, Any]]:
    return _read_store()["exams"]


def create_mark(student_id: str, subject: str, marks: float) -> Dict[str, Any]:
    data = _read_store()
    mark = {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "subject": subject,
        "marks": marks,
        "created_at": _now(),
    }
    data["marks"].append(mark)
    _write_store(data)
    return mark


def list_marks() -> List[Dict[str, Any]]:
    return _read_store()["marks"]


def create_fee_record(student_id: str, kind: str, amount: float, status: str = "pending") -> Dict[str, Any]:
    data = _read_store()
    fee = {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "kind": kind,
        "amount": amount,
        "status": status,
        "created_at": _now(),
    }
    data["fees"].append(fee)
    _write_store(data)
    return fee


def list_fees() -> List[Dict[str, Any]]:
    return _read_store()["fees"]


def create_timetable_entry(day: str, period: str, subject: str, teacher: str, room: str) -> Dict[str, Any]:
    entry = {
        "id": str(uuid.uuid4()),
        "day": day,
        "period": period,
        "subject": subject,
        "teacher": teacher,
        "room": room,
        "created_at": _now(),
    }

    result = _supabase_insert("timetable", entry)
    if result is None:
        raise RuntimeError("Timetable entry was not saved to Supabase.")

    # also keep a local copy for offline workflows
    data = _read_store()
    data["timetable"].append(result)
    _write_store(data)
    return result


def list_timetable() -> List[Dict[str, Any]]:
    return _supabase_get("timetable")


def create_announcement(title: str, body: str, audience: str) -> Dict[str, Any]:
    data = _read_store()
    announcement = {
        "id": str(uuid.uuid4()),
        "title": title,
        "body": body,
        "audience": audience,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("announcements", announcement)
    except Exception:
        supa_row = None

    data["announcements"].append(announcement)
    _write_store(data)
    return supa_row or announcement


def list_announcements() -> List[Dict[str, Any]]:
    return _read_store()["announcements"]


def create_library_book(title: str, author: str, category: str, copies: int) -> Dict[str, Any]:
    data = _read_store()
    book = {
        "id": str(uuid.uuid4()),
        "title": title,
        "author": author,
        "category": category,
        "copies": copies,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("library_books", book)
    except Exception:
        supa_row = None

    data["library_books"].append(book)
    _write_store(data)
    return supa_row or book


def list_library_books() -> List[Dict[str, Any]]:
    return _read_store()["library_books"]


def create_transport_route(name: str, driver: str, route: str, capacity: int) -> Dict[str, Any]:
    transport = {
        "id": str(uuid.uuid4()),
        "name": name,
        "driver": driver,
        "route": route,
        "capacity": int(capacity),
        "created_at": _now(),
    }

    result = _supabase_insert("transport", transport)
    if result is None:
        raise RuntimeError("Transport route was not saved to Supabase.")

    # also persist locally
    data = _read_store()
    data["transport"].append(result)
    _write_store(data)
    return result


def list_transport() -> List[Dict[str, Any]]:
    return _supabase_get("transport")


def create_inventory_item(name: str, category: str, quantity: int, location: str) -> Dict[str, Any]:
    data = _read_store()
    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "quantity": quantity,
        "location": location,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("inventory", item)
    except Exception:
        supa_row = None

    data["inventory"].append(item)
    _write_store(data)
    return supa_row or item


def list_inventory() -> List[Dict[str, Any]]:
    return _read_store()["inventory"]


def create_module(name: str, label: str, description: str, route: str, icon: str, allowed_roles: List[str]) -> Dict[str, Any]:
    data = _read_store()
    module = {
        "id": str(uuid.uuid4()),
        "name": name,
        "label": label,
        "description": description,
        "route": route,
        "icon": icon,
        "allowed_roles": allowed_roles,
        "created_at": _now(),
    }
    supa_row = None
    try:
        supa_row = _supabase_insert("modules", module)
    except Exception:
        supa_row = None

    data["modules"].append(module)
    _write_store(data)
    return supa_row or module


def list_modules() -> List[Dict[str, Any]]:
    return _read_store()["modules"]


def get_dashboard_snapshot() -> Dict[str, Any]:
    data = _read_store()
    return {
        "students": len(data["students"]),
        "teachers": len(data["teachers"]),
        "parents": len(data["parents"]),
        "classes": len(data["classes"]),
        "attendance": len(data["attendance"]),
        "fees": sum(item.get("amount", 0) for item in data["fees"]),
        "announcements": len(data["announcements"]),
        "exams": len(data["exams"]),
    }


def search_records(query: str) -> List[Dict[str, Any]]:
    data = _read_store()
    terms = query.lower()
    results: List[Dict[str, Any]] = []
    for collection_name in ["students", "teachers", "parents", "classes", "library_books", "transport", "inventory", "users"]:
        for item in data.get(collection_name, []):
            payload = " ".join(str(value) for value in item.values()).lower()
            if terms in payload:
                label = item.get("full_name") or item.get("name") or item.get("title") or item.get("email") or item.get("student_id") or item.get("employee_id") or item.get("username") or str(item.get("id"))
                results.append({"type": collection_name, "label": label})
    return results


def export_backup(path: str) -> str:
    data = _read_store()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    return path


def import_backup(path: str) -> None:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    _write_store(data)


def push_local_to_supabase() -> Dict[str, Any]:
    """Push all local records from the JSON store to Supabase.

    Returns a summary dict with pushed counts and any failures. If Supabase
    credentials are not configured this returns a skipped status.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "skipped", "reason": "SUPABASE_URL or SUPABASE_KEY not set"}

    data = _read_store()
    summary: Dict[str, Any] = {"status": "running", "tables": {}}
    for table, records in data.items():
        pushed = 0
        failures: List[Dict[str, Any]] = []
        for record in records:
            try:
                res = _supabase_insert(table, record)
                if res:
                    pushed += 1
                else:
                    failures.append({"id": record.get("id"), "error": "no_response"})
            except Exception as exc:
                failures.append({"id": record.get("id"), "error": str(exc)})
        summary["tables"][table] = {"total": len(records), "pushed": pushed, "failures": len(failures)}

    summary["status"] = "completed"
    return summary
