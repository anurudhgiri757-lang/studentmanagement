import os
import tempfile
import importlib
from pathlib import Path

# Ensure local package imports use project root
import sys
sys.path.insert(0, str(Path('.').resolve()))

# Test 1: register and authenticate
tmp = tempfile.TemporaryDirectory()
os.environ['SCHOOL_DATA_DIR'] = tmp.name
import supabase_client as s
u = s.register_user('Ada Lovelace','ada','ada@example.com','StrongPass123!','1234567890','admin')
assert u['email'] == 'ada@example.com'
auth = s.authenticate_user('ada@example.com','StrongPass123!')
assert auth['email'] == 'ada@example.com'
print('test_register_and_authenticate_user: OK')

# Test 2: create and list students
tmp2 = tempfile.TemporaryDirectory()
os.environ['SCHOOL_DATA_DIR'] = tmp2.name
importlib.reload(s)
st = s.create_student('Ben Carter','STU001','Grade 8','ben@example.com','5551112222','Carol Carter','123 Main St','None')
assert st['student_id'] == 'STU001'
records = s.list_students()
assert len(records) == 1
print('test_create_and_list_students: OK')

# Test 3: create and list teachers
tmp3 = tempfile.TemporaryDirectory()
os.environ['SCHOOL_DATA_DIR'] = tmp3.name
importlib.reload(s)
t = s.create_teacher('Dina Lee','TCH001','Science','MSc','Physics','dina@example.com','5553334444',95000)
assert t['employee_id'] == 'TCH001'
records = s.list_teachers()
assert len(records) == 1
print('test_create_and_list_teachers: OK')

print('ALL TESTS PASSED')
