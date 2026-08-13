import os
import urllib.request
import json
from pathlib import Path

# ensure .env is loaded by supabase_client logic
# reuse env values from .env
def load_env(path: Path):
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, val = line.split('=',1)
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env

env = load_env(Path('.').resolve()/'.env')
SUPABASE_URL = env.get('SUPABASE_URL')
SUPABASE_KEY = env.get('SUPABASE_KEY')

print('Using SUPABASE_URL=', SUPABASE_URL)
print('Using SUPABASE_KEY=', SUPABASE_KEY[:10] + '...' if SUPABASE_KEY else 'MISSING')

def get_table(table):
    url = SUPABASE_URL.rstrip('/') + f"/rest/v1/{table}?select=*"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=10) as fh:
            body = fh.read().decode('utf-8')
            print(f'GET {table} returned:', body[:1000])
    except urllib.error.HTTPError as he:
        print('HTTPError', he, he.read().decode('utf-8') if he.fp else '')
    except Exception as e:
        print('Error', type(e), e)

if __name__ == '__main__':
    for table in ['test_table','students','users','announcements']:
        print('\n===', table, '===')
        get_table(table)

    # Check local db.json
    data_path = Path('data')/ 'db.json'
    print('\nLocal data path:', data_path)
    if data_path.exists():
        print('Local db.json exists, size=', data_path.stat().st_size)
        print(data_path.read_text()[:2000])
    else:
        print('Local db.json not found')
