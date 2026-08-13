import os
import tempfile

from supabase_client import authenticate_user, create_student, create_teacher, list_students, list_teachers, register_user


def test_register_and_authenticate_user(tmp_path):
    os.environ["SCHOOL_DATA_DIR"] = str(tmp_path)
    user = register_user(
        full_name="Ada Lovelace",
        username="ada",
        email="ada@example.com",
        password="StrongPass123!",
        phone="1234567890",
        role="admin",
    )
    assert user["email"] == "ada@example.com"
    auth = authenticate_user("ada@example.com", "StrongPass123!")
    assert auth["email"] == "ada@example.com"


def test_create_and_list_students(tmp_path):
    os.environ["SCHOOL_DATA_DIR"] = str(tmp_path)
    student = create_student(
        full_name="Ben Carter",
        student_id="STU001",
        grade_level="Grade 8",
        email="ben@example.com",
        phone="5551112222",
        guardian_name="Carol Carter",
        address="123 Main St",
        medical_info="None",
    )
    assert student["student_id"] == "STU001"
    records = list_students()
    assert len(records) == 1


def test_create_and_list_teachers(tmp_path):
    os.environ["SCHOOL_DATA_DIR"] = str(tmp_path)
    teacher = create_teacher(
        full_name="Dina Lee",
        employee_id="TCH001",
        department="Science",
        qualification="MSc",
        subject="Physics",
        email="dina@example.com",
        phone="5553334444",
        salary=95000,
    )
    assert teacher["employee_id"] == "TCH001"
    records = list_teachers()
    assert len(records) == 1
