"""
Browser Test - Opens browser windows to test each route
"""

import webbrowser
import time
import subprocess
import sys
import os 
 
def print_colored(text, color='white'):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'white': '\033[0m'
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['white']}")

def open_url(url, delay=1):
    print_colored(f"Opening: {url}", 'blue')
    webbrowser.open(url)
    time.sleep(delay)

def check_server():
    import requests
    try:
        response = requests.get("http://localhost:5000/", timeout=2)
        return True
    except:
        return False

def main():
    print_colored("=" * 60, 'green')
    print_colored("  AI VENTUREFORGE - BROWSER TESTER", 'green')
    print_colored("=" * 60, 'green')
    
    print("\nChecking if server is running...")
    
    if not check_server():
        print_colored("✗ Server is NOT running!", 'red')
        print("\nPlease start your combine.py first:")
        print_colored("  python combine.py", 'yellow')
        print("\nThen run this script again.")
        
        choice = input("\nDo you want to start the server now? (y/n): ")
        if choice.lower() == 'y':
            print_colored("\nStarting server in background...", 'yellow')
            if sys.platform == 'win32':
                subprocess.Popen(['start', 'cmd', '/c', 'python combine.py'], shell=True)
            else:
                subprocess.Popen(['python', 'combine.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print_colored("Waiting 5 seconds for server to start...", 'yellow')
            time.sleep(5)
            
            if not check_server():
                print_colored("✗ Server failed to start. Please start it manually.", 'red')
                return
        else:
            return
    
    print_colored("✓ Server is running!", 'green')
    
    print("\n" + "=" * 60)
    print("  OPENING TEST WINDOWS")
    print("=" * 60)
    
    print("\nOpening main dashboard...")
    open_url("http://localhost:5000/", 2)
    
    print("\nOpening chat page directly...")
    open_url("http://localhost:5000/chat", 2)
    
    print("\nOpening stimulator page directly...")
    open_url("http://localhost:5000/stimulator", 2)
    
    print("\n" + "=" * 60)
    print("  MANUAL TEST INSTRUCTIONS")
    print("=" * 60)
    print("""
1. Check the main dashboard window:
   - Look for the bouncing chat button (bottom right)
   - Click it - should open a modal with chat
   - Click the Stimulator tab in navigation - should open modal

2. Check the direct chat window:
   - Should see a working chat interface
   - Type a message and send
   - Should get a response

3. Check the direct stimulator window:
   - Should see the startup simulator
   - Click "Load Sample Data" button
   - Should see analysis results

4. Press Ctrl+C in the server terminal to stop when done
    """)
    
    print_colored("\nPress Enter to close this tester (server will keep running)...", 'yellow')
    input()

if __name__ == "__main__":
    main()