"""
Detailed System Test - Checks all components individually
"""

import sys
import platform
import subprocess
import importlib.metadata 

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_python_version():
    print_section("Python Environment")
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print(f"Platform: {platform.platform()}")

def test_installed_packages():
    print_section("Installed Packages")
    
    packages = [
        'flask', 'flask_cors', 'requests', 'beautifulsoup4',
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy'
    ]
    
    for package in packages:
        try:
            version = importlib.metadata.version(package.replace('_', '-'))
            print(f"✓ {package}: {version}")
        except:
            print(f"✗ {package}: NOT INSTALLED")

def test_imports():
    print_section("Import Tests")
    
    tests = [
        ('flask', 'Flask'),
        ('flask_cors', 'CORS'),
        ('requests', 'get'),
        ('bs4', 'BeautifulSoup'),
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib', 'plt'),
        ('seaborn', 'sns'),
        ('scipy', 'stats'),
        ('datetime', 'datetime'),
        ('json', 'json'),
        ('base64', 'b64encode'),
        ('io', 'BytesIO'),
        ('warnings', 'warnings')
    ]
    
    for module, alias in tests:
        try:
            if module == 'bs4':
                from bs4 import BeautifulSoup
            else:
                exec(f"import {module}")
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")

def test_file_structure():
    print_section("File Structure")
    
    required_files = ['dashboard.html', 'combine.py']
    
    import os
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} exists ({size} bytes)")
        else:
            print(f"✗ {file} NOT FOUND")

def test_syntax():
    print_section("Syntax Check")
    
    try:
        with open('combine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common syntax errors
        errors = []
        
        # Check for proper route definitions
        if '@app.route' not in content:
            errors.append("No @app.route decorators found")
        
        # Check for main block
        if "if __name__ == '__main__':" not in content:
            errors.append("Missing if __name__ == '__main__' block")
        
        # Check for app.run
        if "app.run" not in content:
            errors.append("Missing app.run() call")
        
        # Check for chat route
        if "@app.route('/chat')" not in content:
            errors.append("Missing /chat route")
        
        # Check for stimulator route
        if "@app.route('/stimulator')" not in content:
            errors.append("Missing /stimulator route")
        
        if errors:
            for error in errors:
                print(f"✗ {error}")
        else:
            print("✓ Basic syntax checks passed")
            
    except FileNotFoundError:
        print("✗ combine.py not found")
    except Exception as e:
        print(f"✗ Error checking syntax: {e}")

def test_port_availability():
    print_section("Port Check")
    
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('localhost', 5000))
        print("✓ Port 5000 is available")
        s.close()
    except socket.error:
        print("✗ Port 5000 is in use")
        print("  Something is already running on port 5000")
        print("  Try: netstat -ano | findstr :5000")

def test_html_files():
    print_section("HTML File Check")
    
    import os
    html_files = ['dashboard.html']
    
    for file in html_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for required elements
            checks = [
                ('chat-bubble', 'Chat button class'),
                ('openChatModal', 'Open chat function'),
                ('openStimulatorModal', 'Open stimulator function'),
                ('/chat', 'Chat route reference'),
                ('/stimulator', 'Stimulator route reference')
            ]
            
            print(f"\nChecking {file}:")
            for check, desc in checks:
                if check in content:
                    print(f"  ✓ {desc} found")
                else:
                    print(f"  ✗ {desc} missing")
        else:
            print(f"✗ {file} not found")

def test_api_connectivity():
    print_section("API Connectivity Test")
    
    import requests
    
    endpoints = [
        ('GET', '/', 'Main page'),
        ('GET', '/chat', 'Chat page'),
        ('GET', '/stimulator', 'Stimulator page'),
        ('POST', '/api/chat', 'Chat API')
    ]
    
    print("\nNote: These tests require the server to be running!")
    print("If server is not running, these will fail.\n")
    
    for method, endpoint, name in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f"http://localhost:5000{endpoint}", timeout=2)
            else:
                response = requests.post(
                    f"http://localhost:5000{endpoint}",
                    json={"message": "test"},
                    timeout=2
                )
            
            if response.status_code == 200:
                print(f"✓ {name} - OK (Status: {response.status_code})")
            else:
                print(f"✗ {name} - Failed (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"✗ {name} - Server not running")
        except requests.exceptions.Timeout:
            print(f"✗ {name} - Timeout")
        except Exception as e:
            print(f"✗ {name} - Error: {e}")

def main():
    print("=" * 60)
    print("  AI VENTUREFORGE - COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    test_python_version()
    test_installed_packages()
    test_imports()
    test_file_structure()
    test_syntax()
    test_port_availability()
    test_html_files()
    
    print("\n" + "=" * 60)
    print("  NEXT STEPS")
    print("=" * 60)
    print("\nIf all checks passed, run:")
    print("  python combine.py")
    print("\nThen run this test again to check API connectivity:")
    print("  python test_detailed.py (after server starts)")
    print("=" * 60)

if __name__ == "__main__":
    main()