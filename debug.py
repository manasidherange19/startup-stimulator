"""
Debug Test - Prints detailed error information
"""

import sys
import traceback

def test_import_with_traceback():
    print("Testing imports with detailed traceback...")
    print("=" * 60)
     
    modules = [
        ('flask', 'Flask'),
        ('flask_cors', 'CORS'),
        ('requests', 'get'),
        ('bs4', 'BeautifulSoup'),
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib', 'plt'),
        ('seaborn', 'sns'),
        ('scipy', 'stats')
    ]
    
    for module_name, alias in modules:
        try:
            if module_name == 'bs4':
                from bs4 import BeautifulSoup
                print(f"✓ {module_name} imported successfully")
            else:
                exec(f"import {module_name}")
                print(f"✓ {module_name} imported successfully")
        except ImportError as e:
            print(f"✗ {module_name} import failed:")
            print(f"  Error: {e}")
            print(f"  Try: pip install {module_name}")
        except Exception as e:
            print(f"✗ {module_name} unexpected error:")
            print(f"  {traceback.format_exc()}")

def test_file_read():
    print("\n" + "=" * 60)
    print("Testing file reads...")
    print("=" * 60)
    
    import os
    
    files = ['combine.py', 'dashboard.html']
    
    for file in files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✓ {file} read successfully ({len(content)} chars)")
                
                # Check for specific patterns
                if file == 'combine.py':
                    patterns = [
                        ("@app.route('/')", "Main route"),
                        ("@app.route('/chat')", "Chat route"),
                        ("@app.route('/stimulator')", "Stimulator route"),
                        ("def chat():", "Chat function"),
                        ("def stimulator():", "Stimulator function"),
                        ("if __name__ == '__main__':", "Main block"),
                        ("app.run", "App run call")
                    ]
                    
                    print(f"\n  Checking {file} patterns:")
                    for pattern, desc in patterns:
                        if pattern in content:
                            print(f"    ✓ {desc} found")
                        else:
                            print(f"    ✗ {desc} MISSING")
                
                if file == 'dashboard.html':
                    patterns = [
                        ("openChatModal", "Chat modal function"),
                        ("openStimulatorModal", "Stimulator modal function"),
                        ("/chat", "Chat route reference"),
                        ("/stimulator", "Stimulator route reference"),
                        ("chat-bubble", "Chat button class")
                    ]
                    
                    print(f"\n  Checking {file} patterns:")
                    for pattern, desc in patterns:
                        if pattern in content:
                            print(f"    ✓ {desc} found")
                        else:
                            print(f"    ✗ {desc} MISSING")
                            
            except Exception as e:
                print(f"✗ Error reading {file}: {e}")
                print(traceback.format_exc())
        else:
            print(f"✗ {file} NOT FOUND in current directory")

def test_environment():
    print("\n" + "=" * 60)
    print("Environment Information...")
    print("=" * 60)
    
    import platform
    import os
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Path: {sys.path}")

def test_manual_server_check():
    print("\n" + "=" * 60)
    print("Manual Server Check Instructions")
    print("=" * 60)
    print("""
To manually check if your server is working:

1. Start your server:
   python combine.py

2. In another terminal, run:
   curl http://localhost:5000/
   (or open in browser)

3. Check that you see:
   - Main dashboard page

4. Check chat route:
   curl http://localhost:5000/chat
   (or open in browser)

5. Check stimulator route:
   curl http://localhost:5000/stimulator
   (or open in browser)

6. Test API:
   curl -X POST http://localhost:5000/api/chat \\
        -H "Content-Type: application/json" \\
        -d '{"message":"Hello"}'
    """)

def main():
    print("=" * 60)
    print("  DEBUG TEST - Detailed Error Analysis")
    print("=" * 60)
    
    test_environment()
    test_import_with_traceback()
    test_file_read()
    test_manual_server_check()
    
    print("\n" + "=" * 60)
    print("  DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()