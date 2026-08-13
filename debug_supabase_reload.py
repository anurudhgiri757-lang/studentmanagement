import os
import importlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').resolve()))

# Clear any existing SUPABASE_* vars so load_dotenv can set from .env
for k in ('SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_ROLE'):
    os.environ.pop(k, None)

import supabase_client as s
importlib.reload(s)

print('SUPABASE_URL=', s.SUPABASE_URL)
print('SUPABASE_KEY=', s.SUPABASE_KEY[:10] + '...' if s.SUPABASE_KEY else 'MISSING')
print('SUPABASE_SERVICE_ROLE=', bool(s.SUPABASE_SERVICE_ROLE))
try:
    print('dotenv_path=', s.dotenv_path)
    if s.dotenv_path.exists():
        txt = s.dotenv_path.read_text()
        print('.env content read by module:\n', txt)
    else:
        print('.env path does not exist')
except Exception as e:
    print('error reading dotenv_path:', e)

try:
    res = s._supabase_insert('test_table', {'id':'debug-test'})
    print('insert result:', res)
except Exception as e:
    print('caught exception:', type(e), e)
