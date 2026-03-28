"""
Route Testing Script - Tests all routes programmatically
"""

import requests
import json 
import time

BASE_URL = "http://localhost:5000"

class RouteTester:
    def __init__(self):
        self.results = []
        self.server_running = False
    
    def print_header(self, text):
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_result(self, test_name, passed, message=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        color = "\033[92m" if passed else "\033[91m"
        print(f"{color}{status}\033[0m - {test_name}")
        if message:
            print(f"    {message}")
        self.results.append(passed)
    
    def check_server(self):
        print("Checking if server is running...")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                self.print_result("Server Status", True, "Server is running")
                self.server_running = True
                return True
            else:
                self.print_result("Server Status", False, f"Server returned status {response.status_code}")
                return False
        except:
            self.print_result("Server Status", False, "Cannot connect to server")
            return False
    
    def test_get_route(self, route, name):
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            if response.status_code == 200:
                content_length = len(response.text)
                self.print_result(name, True, f"Status 200, Content length: {content_length} bytes")
                return True
            else:
                self.print_result(name, False, f"Status {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            self.print_result(name, False, "Timeout")
            return False
        except Exception as e:
            self.print_result(name, False, str(e))
            return False
    
    def test_post_route(self, route, name, data=None):
        try:
            if data is None:
                data = {"message": "Test message from route tester"}
            
            response = requests.post(
                f"{BASE_URL}{route}",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if 'response' in response_data:
                        self.print_result(name, True, f"Got response: {response_data['response'][:50]}...")
                    else:
                        self.print_result(name, True, f"Status 200, Response keys: {list(response_data.keys())}")
                    return True
                except:
                    self.print_result(name, True, f"Status 200, Response: {response.text[:100]}")
                    return True
            else:
                self.print_result(name, False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.print_result(name, False, str(e))
            return False
    
    def test_content_type(self, route, name, expected_type):
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            content_type = response.headers.get('Content-Type', '')
            
            if expected_type in content_type:
                self.print_result(name, True, f"Content-Type: {content_type}")
                return True
            else:
                self.print_result(name, False, f"Expected {expected_type}, got {content_type}")
                return False
        except Exception as e:
            self.print_result(name, False, str(e))
            return False
    
    def test_chat_functionality(self):
        print("\nTesting chat functionality...")
        
        test_messages = [
            "Hello",
            "How are you?",
            "What can you do?",
            "Tell me about AI"
        ]
        
        for msg in test_messages:
            try:
                response = requests.post(
                    f"{BASE_URL}/api/chat",
                    json={"message": msg},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data and len(data['response']) > 0:
                        print(f"  ✓ Message '{msg}' - Got response ({len(data['response'])} chars)")
                    else:
                        print(f"  ✗ Message '{msg}' - Invalid response format")
                else:
                    print(f"  ✗ Message '{msg}' - Status {response.status_code}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  ✗ Message '{msg}' - Error: {e}")
    
    def test_stimulator_endpoints(self):
        print("\nTesting stimulator endpoints...")
        
        endpoints = [
            ('GET', '/api/generate_sample', 'Generate sample data'),
            ('POST', '/api/analyze_manual', 'Manual analysis')
        ]
        
        for method, endpoint, name in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                else:
                    test_data = {
                        "revenue": 50000,
                        "users": 1000,
                        "cac": 75,
                        "churn": 5,
                        "nps": 60,
                        "growth": 15,
                        "burn": 30000
                    }
                    response = requests.post(f"{BASE_URL}{endpoint}", json=test_data, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        health_score = data.get('health', {}).get('health_score', 'N/A')
                        print(f"  ✓ {name} - Health score: {health_score}")
                    else:
                        print(f"  ✗ {name} - API returned success=False: {data.get('error', 'Unknown error')}")
                else:
                    print(f"  ✗ {name} - Status {response.status_code}")
            except Exception as e:
                print(f"  ✗ {name} - Error: {e}")
    
    def run_all_tests(self):
        self.print_header("ROUTE TESTING SUITE")
        
        if not self.check_server():
            print("\nCannot continue without server. Please start combine.py first.")
            return False
        
        self.print_header("GET ROUTE TESTS")
        
        # Test main routes
        self.test_get_route('/', 'Main page (/)')
        self.test_get_route('/chat', 'Chat page (/chat)')
        self.test_get_route('/stimulator', 'Stimulator page (/stimulator)')
        
        self.print_header("CONTENT TYPE TESTS")
        
        self.test_content_type('/', 'Main page content type', 'text/html')
        self.test_content_type('/chat', 'Chat page content type', 'text/html')
        self.test_content_type('/stimulator', 'Stimulator page content type', 'text/html')
        
        self.print_header("API ENDPOINT TESTS")
        
        self.test_post_route('/api/chat', 'Chat API endpoint')
        
        self.print_header("FUNCTIONALITY TESTS")
        
        self.test_chat_functionality()
        self.test_stimulator_endpoints()
        
        self.print_header("TEST SUMMARY")
        
        total = len(self.results)
        passed = sum(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your application is working correctly!")
        else:
            print("\n⚠️ Some tests failed.")
            print("Check the output above for details.")
        
        return passed == total

if __name__ == "__main__":
    tester = RouteTester()
    tester.run_all_tests()