"""
Test imports - Run this first to check if all required packages are installed
"""

print("=" * 50)
print("Testing Python Imports...")
print("=" * 50)

# List of required packages
required_packages = [
    'flask',
    'flask_cors',
    'requests',
    'bs4',
    'pandas', 
    'numpy',
    'matplotlib',
    'seaborn',
    'scipy',
    'datetime',
    'urllib',
    'io',
    'base64',
    'warnings',
    'traceback'
]

failed = []

for package in required_packages:
    try:
        if package == 'bs4':
            exec(f"from bs4 import BeautifulSoup")
        else:
            exec(f"import {package}")
        print(f"✓ {package} - OK")
    except ImportError as e:
        print(f"✗ {package} - FAILED: {e}")
        failed.append(package)

print("\n" + "=" * 50)
if failed:
    print(f"❌ Missing packages: {', '.join(failed)}")
    print("\nInstall them with:")
    print(f"pip install {' '.join(failed)}")
else:
    print("✅ All packages installed successfully!")
print("=" * 50)