# check_urls.py
from django.urls import get_resolver
from django.conf import settings

# Setup Django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
import django
django.setup()

def show_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # It's an included URLconf
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            # It's a single URL
            try:
                name = pattern.name if pattern.name else 'No name'
                print(f"{prefix}{pattern.pattern} -> {name} (namespace: dashboard)")
            except:
                print(f"{prefix}{pattern.pattern} -> No name")

print("\n=== REGISTERED URLS ===\n")
show_urls(get_resolver().url_patterns)
print("\n=======================\n")