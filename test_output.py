# test_output.py
import sys
import os

print("=== DIRECT PRINT TEST ===")
print("This should appear immediately")

sys.stdout.write("=== STDOUT WRITE TEST ===\n")
sys.stdout.flush()

sys.stderr.write("=== STDERR WRITE TEST ===\n")
sys.stderr.flush()

# Test Django output
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
import django
django.setup()

print("Django setup complete - this should also appear")
