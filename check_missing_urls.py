import os
import re
from pathlib import Path


def extract_urls_from_templates(templates_dir):
    """Extract all {% url %} tags from HTML templates"""
    url_names = set()
    pattern = r"{%\s+url\s+['\"]([^'\"]+)['\"]"

    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    found = re.findall(pattern, content)
                    url_names.update(found)
                    if found:
                        print(f"  Found in {filepath}: {found}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    return url_names


def extract_urls_from_urls_file(urls_file):
    """Extract all URL names from urls.py"""
    url_names = set()
    pattern = r"name=['\"]([^'\"]+)['\"]"

    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        url_names.update(re.findall(pattern, content))
    except Exception as e:
        print(f"Error reading {urls_file}: {e}")

    return url_names


def extract_view_names(views_file):
    """Extract all view function names from views.py"""
    view_names = set()
    pattern = r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("

    try:
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        view_names.update(re.findall(pattern, content, re.MULTILINE))
    except Exception as e:
        print(f"Error reading {views_file}: {e}")

    return view_names


def main():
    print("=" * 70)
    print("MISSING URL PATTERNS CHECKER")
    print("=" * 70)

    # Define paths
    templates_dir = "dashboard/templates"
    urls_file = "dashboard/urls.py"
    views_file = "dashboard/views.py"

    print(f"\n📁 Scanning templates in: {templates_dir}")
    print(f"📄 URLS file: {urls_file}")
    print(f"📄 Views file: {views_file}")
    print("-" * 70)

    # Extract data
    print("\n🔍 Extracting URL references from templates...")
    template_urls = extract_urls_from_templates(templates_dir)

    print("\n🔍 Extracting URL patterns from urls.py...")
    defined_urls = extract_urls_from_urls_file(urls_file)

    print("\n🔍 Extracting view functions from views.py...")
    view_functions = extract_view_names(views_file)

    # Find missing URLs
    missing_urls = template_urls - defined_urls

    # Find views that are referenced but missing
    missing_views = defined_urls - view_functions

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\n📊 STATISTICS:")
    print(f"   URL references in templates: {len(template_urls)}")
    print(f"   URL patterns defined in urls.py: {len(defined_urls)}")
    print(f"   View functions in views.py: {len(view_functions)}")

    print(f"\n❌ MISSING URL PATTERNS (in templates but not in urls.py):")
    if missing_urls:
        for i, url in enumerate(sorted(missing_urls), 1):
            print(f"   {i}. {url}")

        # Generate code for missing URLs
        print("\n" + "=" * 70)
        print("📝 CODE TO ADD TO urls.py:")
        print("=" * 70)
        for url in sorted(missing_urls):
            url_path = url.replace('_', '-')
            print(f"    path('{url_path}/', views.{url}, name='{url}'),")
    else:
        print("   ✅ None found!")

    print(f"\n⚠️  MISSING VIEW FUNCTIONS (in urls.py but not in views.py):")
    if missing_views:
        for i, view in enumerate(sorted(missing_views), 1):
            print(f"   {i}. {view}")

        # Generate code for missing views
        print("\n" + "=" * 70)
        print("📝 CODE TO ADD TO views.py:")
        print("=" * 70)
        for view in sorted(missing_views):
            print(f"""
def {view}(request):
    from django.shortcuts import render
    return render(request, 'dashboard/dashboard.html', {{'title': '{view.replace('_', ' ').title()}'}})
""")
    else:
        print("   ✅ None found!")

    # Find unused views
    used_views = set()
    for url in template_urls:
        if url in view_functions:
            used_views.add(url)

    unused_views = view_functions - defined_urls - {'handler404', 'handler500'}
    # Remove internal/system views that might not need URLs
    internal_views = {'test_template', 'test_session', 'debug_login', 'debug_cloudinary',
                      'debug_faculty_data', 'is_cloudinary_configured', 'get_file_from_field',
                      'convert_pdf_to_images', 'merge_all_documents', 'merge_documents',
                      'merge_files', 'collect_faculty_files', 'generate_faculty_pdf_bytes',
                      'merge_certificates_with_pdf_bytes', 'process_csv_faculty_data',
                      'generate_student_pdf', 'merge_files_legacy'}

    unused_views = unused_views - internal_views

    print(f"\n📌 UNUSED VIEWS (defined but no URL pattern):")
    if unused_views:
        for i, view in enumerate(sorted(unused_views), 1):
            print(f"   {i}. {view}")
    else:
        print("   ✅ None found!")

    print("\n" + "=" * 70)
    print("COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()