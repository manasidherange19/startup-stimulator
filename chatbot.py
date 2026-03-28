"""
Professional AI Assistant - Same Stunning Animation as Dashboard
Run with: python app.py
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import stimulator

app = Flask(__name__)
CORS(app)

# DuckDuckGo Search Implementation
class DuckDuckGoSearch:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def search(self, query, max_results=2):
        """Search DuckDuckGo and return relevant information"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            result_elements = soup.find_all('div', class_='result')[:max_results]
            
            for elem in result_elements:
                title_elem = elem.find('a', class_='result__a')
                snippet_elem = elem.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    
                    results.append({
                        'title': title,
                        'snippet': snippet
                    })
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_answer(self, query):
        """Get comprehensive answer from search results"""
        results = self.search(query, max_results=2)
        
        if not results:
            return None
        
        answer = ""
        for i, result in enumerate(results, 1):
            answer += f"📌 **{result['title']}**\n{result['snippet']}\n\n"
        
        return answer.strip()

# Initialize search
search_engine = DuckDuckGoSearch()

# Simple, clean responses for common queries
def get_response(user_input):
    """Generate natural, helpful responses"""
    user_input_lower = user_input.lower().strip()
    
    # Greetings
    if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
        responses = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! What would you like to know?"
        ]
        return random.choice(responses)
    
    # How are you
    if any(phrase in user_input_lower for phrase in ['how are you', 'how are you doing', 'how do you do']):
        responses = [
            "I'm doing great, thanks for asking! How can I assist you?",
            "All good here! What can I help you with?",
            "Doing well! What's on your mind?"
        ]
        return random.choice(responses)
    
    # Thanks
    if any(word in user_input_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
        responses = [
            "You're welcome! Happy to help. Anything else?",
            "My pleasure! Let me know if you need anything else.",
            "Glad I could help! What else can I do for you?"
        ]
        return random.choice(responses)
    
    # Goodbye
    if any(word in user_input_lower for word in ['bye', 'goodbye', 'see you', 'farewell', 'take care']):
        responses = [
            "Goodbye! Feel free to come back anytime.",
            "Take care! Have a great day.",
            "Bye! Happy to help whenever you need."
        ]
        return random.choice(responses)
    
    # Help
    if user_input_lower in ['help', 'help me', 'what can you do', 'what do you do']:
        return """I can help you with:
• Answering questions on any topic
• Finding information online
• Startup and business advice
• General knowledge questions

Just ask me anything, and I'll do my best to help!"""
    
    # For everything else, search the web
    print(f"Searching for: {user_input}")
    search_results = search_engine.get_answer(user_input)
    
    if search_results:
        return f"{search_results}\n\nIs there anything specific you'd like to know more about?"
    else:
        # Fallback for when search fails
        fallbacks = [
            f"I understand you're asking about: {user_input}\n\nI want to help you with that. Could you provide a bit more detail so I can give you the best answer?",
            
            f"Thanks for your question! To give you the most helpful answer, could you tell me a bit more about what you're looking for?",
            
            f"I'm here to help with your question about: {user_input}\n\nWould you mind rephrasing or giving me more context? I want to make sure I understand correctly."
        ]
        return random.choice(fallbacks)

# HTML Template - SAME STUNNING BACKGROUND as original dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>AI Assistant - Professional Chatbot</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #05050f;
            overflow-x: hidden;
            color: #fff;
            min-height: 100vh;
        }

        /* Particle Animation Canvas - SAME AS ORIGINAL */
        #particleCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            pointer-events: none;
        }

        /* Animated Gradient Background - SAME AS ORIGINAL */
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(circle at 20% 30%, rgba(0, 100, 255, 0.15), rgba(0, 0, 0, 0.95));
            animation: bgPulse 8s ease-in-out infinite;
        }

        @keyframes bgPulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }

        /* Floating Orbs - SAME AS ORIGINAL */
        .orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(80px);
            z-index: -1;
            pointer-events: none;
            animation: float 20s infinite ease-in-out;
        }

        .orb-1 {
            width: 500px;
            height: 500px;
            background: rgba(0, 200, 255, 0.1);
            top: -200px;
            right: -200px;
            animation-delay: 0s;
        }

        .orb-2 {
            width: 600px;
            height: 600px;
            background: rgba(255, 0, 200, 0.08);
            bottom: -300px;
            left: -200px;
            animation-delay: -5s;
        }

        .orb-3 {
            width: 400px;
            height: 400px;
            background: rgba(100, 0, 255, 0.12);
            top: 50%;
            left: 50%;
            animation-delay: -10s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(50px, -50px) scale(1.1); }
            66% { transform: translate(-30px, 30px) scale(0.9); }
        }

        /* Main Container */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem;
            position: relative;
            z-index: 2;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeInUp 1s ease;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #00ffea, #ff00e0, #00aaff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
            animation: gradientShift 3s ease infinite;
            background-size: 200% 200%;
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .header p {
            color: #aaa;
            font-size: 1rem;
        }

        /* Chat Box */
        .chat-box {
            background: rgba(20, 30, 45, 0.4);
            backdrop-filter: blur(20px);
            border-radius: 2rem;
            border: 1px solid rgba(0, 255, 255, 0.2);
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
            animation: slideInLeft 0.8s ease;
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .chat-header {
            background: linear-gradient(135deg, rgba(0, 100, 255, 0.3), rgba(0, 0, 0, 0.5));
            padding: 1.2rem 1.5rem;
            border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        }

        .chat-header h2 {
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status {
            font-size: 0.75rem;
            color: #0f0;
            display: flex;
            align-items: center;
            gap: 5px;
            margin-top: 0.3rem;
        }

        .chat-messages {
            height: 500px;
            overflow-y: auto;
            padding: 1.5rem;
        }

        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(0, 255, 255, 0.5);
            border-radius: 10px;
        }

        .message {
            margin-bottom: 1rem;
            animation: messageSlide 0.3s ease;
        }

        @keyframes messageSlide {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .user-message {
            text-align: right;
        }

        .bot-message {
            text-align: left;
        }

        .user-message .message-content {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            display: inline-block;
            padding: 0.8rem 1.2rem;
            border-radius: 1.5rem;
            max-width: 80%;
            text-align: left;
            box-shadow: 0 5px 15px rgba(0, 114, 255, 0.3);
        }

        .bot-message .message-content {
            background: rgba(30, 40, 60, 0.9);
            display: inline-block;
            padding: 0.8rem 1.2rem;
            border-radius: 1.5rem;
            max-width: 90%;
            border-left: 3px solid #00ffea;
            white-space: pre-wrap;
            text-align: left;
        }

        .message-content {
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .message-time {
            font-size: 0.7rem;
            color: #888;
            margin-top: 0.2rem;
        }

        .chat-input-area {
            padding: 1.2rem;
            border-top: 1px solid rgba(0, 255, 255, 0.2);
            display: flex;
            gap: 1rem;
            background: rgba(0, 0, 0, 0.3);
        }

        .chat-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 50px;
            padding: 0.8rem 1.2rem;
            font-family: inherit;
            font-size: 0.95rem;
            color: white;
            outline: none;
            transition: all 0.3s;
        }

        .chat-input:focus {
            border-color: #00ffea;
            box-shadow: 0 0 20px rgba(0, 255, 234, 0.2);
        }

        .send-btn {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border: none;
            border-radius: 50px;
            padding: 0 1.5rem;
            font-family: inherit;
            font-weight: bold;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .send-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 198, 255, 0.5);
        }

        .suggestions {
            padding: 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            border-top: 1px solid rgba(0, 255, 255, 0.1);
        }

        .suggestion-chip {
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 50px;
            padding: 0.4rem 1rem;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s;
            color: #fff;
        }

        .suggestion-chip:hover {
            background: rgba(0, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        .typing-indicator {
            display: inline-block;
            padding: 0.8rem 1.2rem;
            background: rgba(30, 40, 60, 0.9);
            border-radius: 1.5rem;
            border-left: 3px solid #00ffea;
        }

        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ffea;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }

        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30% { transform: translateY(-10px); opacity: 1; }
        }

        footer {
            text-align: center;
            margin-top: 1.5rem;
            padding: 1rem;
            color: #666;
            font-size: 0.75rem;
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            .header h1 {
                font-size: 1.8rem;
            }
            .chat-messages {
                height: 400px;
            }
        }
    </style>
</head>
<body>
    <canvas id="particleCanvas"></canvas>
    <div class="animated-bg"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> AI Assistant</h1>
            <p>Ask me anything - I'll help you find answers</p>
        </div>

        <div class="chat-box">
            <div class="chat-header">
                <h2><i class="fas fa-comments"></i> Smart Assistant <span style="font-size: 0.7rem; background: rgba(0,255,0,0.2); padding: 2px 8px; border-radius: 20px; margin-left: 10px;"><i class="fas fa-search"></i> Web Search Active</span></h2>
                <div class="status">
                    <i class="fas fa-circle" style="color: #0f0; font-size: 0.6rem;"></i> Online | Ready to help
                </div>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <div class="message-content">
Hello! I'm your AI assistant. I can help answer your questions, find information, and assist with various topics.<br><br>
What would you like to know?
                    </div>
                    <div class="message-time">Just now</div>
                </div>
            </div>
            <div class="suggestions">
                <div class="suggestion-chip" data-question="What can you help me with?">❓ What can you help with?</div>
                <div class="suggestion-chip" data-question="Tell me about artificial intelligence">🤖 AI Explained</div>
                <div class="suggestion-chip" data-question="How to start a business?">💼 Business Advice</div>
                <div class="suggestion-chip" data-question="Tell me a fun fact">✨ Fun Fact</div>
                <div class="suggestion-chip" data-question="What's the latest news?">📰 Latest News</div>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="Type your message here...">
                <button class="send-btn" id="sendBtn">
                    <i class="fas fa-paper-plane"></i> Send
                </button>
            </div>
        </div>
        
        <footer>
            <i class="fas fa-brain"></i> AI-Powered with Web Search | Natural Language Processing
        </footer>
    </div>

    <script>
        // Particle Animation System - SAME AS ORIGINAL DASHBOARD
        const canvas = document.getElementById('particleCanvas');
        const ctx = canvas.getContext('2d');
        let width = window.innerWidth;
        let height = window.innerHeight;
        let particles = [];
        const PARTICLE_COUNT = 150;

        function resizeCanvas() {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        }

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.3;
                this.radius = Math.random() * 2 + 1;
                this.color = `hsl(${Math.random() * 60 + 180}, 100%, 60%)`;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0) this.x = width;
                if (this.x > width) this.x = 0;
                if (this.y < 0) this.y = height;
                if (this.y > height) this.y = 0;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        function initParticles() {
            particles = [];
            for (let i = 0; i < PARTICLE_COUNT; i++) {
                particles.push(new Particle());
            }
        }

        function animateParticles() {
            if (!ctx) return;
            ctx.clearRect(0, 0, width, height);
            for (let p of particles) {
                p.update();
                p.draw();
            }
            // Draw connections
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < 100) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(0, 200, 255, ${0.1 * (1 - dist / 100)})`;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animateParticles);
        }

        window.addEventListener('resize', () => {
            resizeCanvas();
            initParticles();
        });

        resizeCanvas();
        initParticles();
        animateParticles();

        // Chat Functionality
        function addMessage(message, isUser) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            let formattedMessage = message
                .replace(/\\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/•/g, '•');
            
            messageDiv.innerHTML = `
                <div class="message-content">${formattedMessage}</div>
                <div class="message-time">${time}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTyping() {
            const chatMessages = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = `
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            `;
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function removeTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(escapeHtml(message), true);
            input.value = '';
            input.disabled = true;
            
            showTyping();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                removeTyping();
                addMessage(data.response, false);
                
            } catch (error) {
                removeTyping();
                addMessage("I'm having trouble connecting. Please check your connection and try again.", false);
            }
            
            input.disabled = false;
            input.focus();
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Event Listeners
        document.getElementById('sendBtn').addEventListener('click', sendMessage);
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Suggestion chips
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.getElementById('chatInput').value = chip.getAttribute('data-question');
                sendMessage();
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with natural responses"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get natural response
    response = get_response(user_message)
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'web_search_enabled': True
    })
@app.route('/stimulator')
def run_stimulator():
    result = stimulator.run_simulation()   # 👈 function from your file
    return result

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🤖 Professional AI Assistant - Ready to Help!        ║
    ║                                                          ║
    ║  Server running at: http://localhost:5000                ║
    ║                                                          ║
    ║  Features:                                               ║
    ║  • Natural conversation                                  ║
    ║  • Web search for accurate answers                       ║
    ║  • Same stunning animation as dashboard                  ║
    ║  • Clean, professional interface                         ║
    ║                                                          ║
    ║  Just ask anything!                                      ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)

