import importlib
import supabase_client as s
importlib.reload(s)

res = s.push_local_to_supabase()
print('push summary:', res)
