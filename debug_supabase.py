import supabase_client as s

print('SUPABASE_URL=', s.SUPABASE_URL)
print('SUPABASE_KEY=', s.SUPABASE_KEY[:10] + '...' if s.SUPABASE_KEY else 'MISSING')

try:
    res = s._supabase_insert('test_table', {'id':'debug-test'})
    print('insert result:', res)
except Exception as e:
    print('caught exception:', type(e), e)
