# install_requirements.py
import subprocess
import sys


def install_packages():
    packages = [
        'six==1.16.0',
        'cloudinary==1.44.1',
        'django-cloudinary-storage==0.3.0',
        'requests==2.31.0',
        'Pillow==10.1.0',
        'PyPDF2==3.0.1',
        'reportlab==4.0.4'
    ]

    print("Installing required packages...")
    print("=" * 60)

    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")

    print("\n" + "=" * 60)
    print("Installation complete!")
    print("\nNext steps:")
    print("1. Restart PyCharm")
    print("2. Run: python manage.py runserver")


if __name__ == "__main__":
    install_packages()