"""
Test Flask Server - Check if basic routes are working
Run with: python test_server.py
"""

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Simple HTML for testing
TEST_HTML = '''
<!DOCTYPE html>
<html> 
<head>
    <title>Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            text-align: center;
            padding: 50px;
        }
        .success {
            background: #00ff9d20;
            border: 2px solid #00ff9d;
            border-radius: 10px;
            padding: 20px;
            margin: 20px auto;
            max-width: 600px;
        }
        .test-btn {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            margin: 10px;
        }
        .test-btn:hover {
            transform: scale(1.05);
        }
        .route-status {
            background: #333;
            border-radius: 5px;
            padding: 10px;
            margin: 10px auto;
            max-width: 500px;
            text-align: left;
        }
        .status-ok { color: #00ff9d; }
        .status-bad { color: #ff4444; }
    </style>
</head>
<body>
    <h1>🧪 Flask Server Test</h1>
    <div class="success">
        <h2>✅ Server is running!</h2>
        <p>Flask is working correctly on port 5000</p>
    </div>
    
    <h3>Test Routes:</h3>
    <div class="route-status">
        <strong>Main Page:</strong> <span id="main-status">Testing...</span>
        <button class="test-btn" onclick="testRoute('/')">Test /</button>
    </div>
    <div class="route-status">
        <strong>Chat Route:</strong> <span id="chat-status">Testing...</span>
        <button class="test-btn" onclick="testRoute('/chat')">Test /chat</button>
    </div>
    <div class="route-status">
        <strong>Stimulator Route:</strong> <span id="stimulator-status">Testing...</span>
        <button class="test-btn" onclick="testRoute('/stimulator')">Test /stimulator</button>
    </div>
    <div class="route-status">
        <strong>API Chat:</strong> <span id="api-status">Testing...</span>
        <button class="test-btn" onclick="testAPI()">Test /api/chat</button>
    </div>
    
    <script>
        async function testRoute(route) {
            try {
                const response = await fetch(route);
                const status = response.ok ? '✅ Working' : '❌ Failed';
                const statusElement = document.getElementById(route === '/' ? 'main-status' : 
                                                            route === '/chat' ? 'chat-status' : 'stimulator-status');
                if (statusElement) {
                    statusElement.innerHTML = status;
                    statusElement.className = response.ok ? 'status-ok' : 'status-bad';
                }
                if (response.ok) {
                    alert(`Route ${route} is working! Status: ${response.status}`);
                } else {
                    alert(`Route ${route} returned status: ${response.status}`);
                }
            } catch (error) {
                alert(`Error testing ${route}: ${error.message}`);
            }
        }
        
        async function testAPI() {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: 'Hello' })
                });
                const data = await response.json();
                const statusElement = document.getElementById('api-status');
                if (response.ok && data.response) {
                    statusElement.innerHTML = '✅ Working';
                    statusElement.className = 'status-ok';
                    alert(`API is working!\nResponse: ${data.response.substring(0, 100)}...`);
                } else {
                    statusElement.innerHTML = '❌ Failed';
                    statusElement.className = 'status-bad';
                    alert('API returned unexpected response');
                }
            } catch (error) {
                document.getElementById('api-status').innerHTML = '❌ Failed';
                alert(`Error testing API: ${error.message}`);
            }
        }
        
        // Auto-test on load
        setTimeout(() => {
            testRoute('/');
            testRoute('/chat');
            testRoute('/stimulator');
            testAPI();
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(TEST_HTML)

@app.route('/chat')
def chat():
    return "<h1>✅ Chat Route Working!</h1><p>This is the chat interface placeholder. Your combine.py should show the full chat interface here.</p>"

@app.route('/stimulator')
def stimulator():
    return "<h1>✅ Stimulator Route Working!</h1><p>This is the stimulator interface placeholder. Your combine.py should show the full stimulator interface here.</p>"

@app.route('/api/chat', methods=['POST'])
def test_chat():
    from flask import request
    data = request.json
    return jsonify({'response': f"Test response to: {data.get('message', '')} - API is working!"})

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 Test Server Started!")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("\nThis test server will check if:")
    print("  ✓ Flask is running properly")
    print("  ✓ Basic routes are accessible")
    print("  ✓ API endpoint is working")
    print("\nPress Ctrl+C to stop the test server")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)