from pathlib import Path
print('cwd', Path('.').resolve())
path = Path('.env').resolve()
print('env exists', path.exists())
print('env content:', repr(path.read_text() if path.exists() else ''))
import supabase_client
print('SUPABASE_URL', supabase_client.SUPABASE_URL)
print('SUPABASE_KEY', supabase_client.SUPABASE_KEY[:10] + '...' if supabase_client.SUPABASE_KEY else 'MISSING')
