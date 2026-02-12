# test_install.py
import sys

print("Checking if required packages are installed...")
print("=" * 60)

# Check six
try:
    import six
    print("✓ six module installed")
    print(f"  Version: {six.__version__}")
except ImportError:
    print("✗ six NOT installed")
    print("  Run: pip install six")

# Check cloudinary
try:
    import cloudinary
    print("✓ cloudinary module installed")
    print(f"  Version: {cloudinary.__version__}")
except ImportError:
    print("✗ cloudinary NOT installed")
    print("  Run: pip install cloudinary")

# Check cloudinary_storage
try:
    import cloudinary_storage
    print("✓ cloudinary_storage module installed")
except ImportError:
    print("✗ cloudinary_storage NOT installed")
    print("  Run: pip install django-cloudinary-storage")

print("\n" + "=" * 60)
print("Summary:")

if 'six' in sys.modules and 'cloudinary' in sys.modules:
    print("✅ All required packages are installed!")
    print("\nNow restart your Django server:")
    print("python manage.py runserver")
else:
    print("❌ Some packages are missing.")
    print("\nPlease run:")
    print("pip install six cloudinary django-cloudinary-storage")