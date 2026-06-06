import os
import dj_database_url
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
print(dj_database_url.parse(os.environ['DATABASE_URL']))
