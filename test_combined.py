"""
Test Combined Application - Run this with your actual combine.py
This script tests if your combined application is working correctly
"""

import requests 
import json
import sys

BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_route(route, description):
    print(f"\nTesting {description}...")
    try:
        response = requests.get(f"{BASE_URL}{route}", timeout=5)
        if response.status_code == 200:
            print(f"  ✓ {description} - OK (Status: {response.status_code})")
            return True
        else:
            print(f"  ✗ {description} - Failed (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ {description} - Cannot connect to server!")
        print("    Make sure your combine.py is running on port 5000")
        return False
    except Exception as e:
        print(f"  ✗ {description} - Error: {e}")
        return False

def test_api():
    print("\nTesting API Endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "Hello, are you working?"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print(f"  ✓ API Working!")
                print(f"    Response: {data['response'][:100]}...")
                return True
            else:
                print(f"  ✗ API returned unexpected response format")
                return False
        else:
            print(f"  ✗ API Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"  ✗ API Error: {e}")
        return False

def main():
    print_header("Testing Combined Application")
    
    print("\nFirst, make sure your combine.py is running!")
    print("If not, run: python combine.py in another terminal")
    print("\nWaiting for server...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print("✓ Server is running!")
    except:
        print("✗ Server is NOT running!")
        print("\nPlease start your combine.py first:")
        print("  python combine.py")
        print("\nThen run this test again.")
        return
    
    print_header("Testing Routes")
    
    tests = [
        ("/", "Main Page"),
        ("/chat", "Chat Page"),
        ("/stimulator", "Stimulator Page")
    ]
    
    results = []
    for route, desc in tests:
        result = test_route(route, desc)
        results.append(result)
    
    api_result = test_api()
    results.append(api_result)
    
    print_header("Summary")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n  Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✓ ALL TESTS PASSED!")
        print("  Your combined application is working correctly!")
        print("\n  You can now open: http://localhost:5000")
    else:
        print("\n  ✗ Some tests failed!")
        print("\n  Check:")
        if not results[0]:
            print("    - Main page route (/) is not working")
        if not results[1]:
            print("    - Chat route (/chat) is not working")
        if not results[2]:
            print("    - Stimulator route (/stimulator) is not working")
        if not results[3]:
            print("    - API endpoint (/api/chat) is not working")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()