# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
import django
django.setup()

db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add missing columns
    cursor.execute("PRAGMA table_info(dashboard_faculty)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Current columns:", columns)
    
    missing = ['caste', 'sub_caste', 'nationality', 'jntuh_id', 'aicte_id', 'orcid_id']
    for col in missing:
        if col not in columns:
            print(f"Adding {col}...")
            cursor.execute(f"ALTER TABLE dashboard_faculty ADD COLUMN {col} VARCHAR(100) NULL")
    
    conn.commit()
    print("✅ Database fixed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()