"""
Combined AI Assistant + Startup Performance Simulator
Run with: python combine.py
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import urllib.parse 
import pandas as pd
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import traceback
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Set style for plots
plt.style.use('dark_background')
sns.set_palette("husl")

# ============================================
# CHATBOT MODULE
# ============================================

class DuckDuckGoSearch:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def search(self, query, max_results=2):
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
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True)
                    })
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_answer(self, query):
        results = self.search(query, max_results=2)
        if not results:
            return None
        answer = ""
        for result in results:
            answer += f"📌 **{result['title']}**\n{result['snippet']}\n\n"
        return answer.strip()

search_engine = DuckDuckGoSearch()

def get_response(user_input):
    user_input_lower = user_input.lower().strip()
    
    if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return random.choice(["Hello! How can I help you today?", "Hi there! What can I do for you?"])
    
    if any(phrase in user_input_lower for phrase in ['how are you', 'how are you doing']):
        return random.choice(["I'm doing great, thanks for asking! How can I assist you?", "All good here! What can I help you with?"])
    
    if any(word in user_input_lower for word in ['thank', 'thanks']):
        return random.choice(["You're welcome! Happy to help.", "My pleasure! Let me know if you need anything else."])
    
    if any(word in user_input_lower for word in ['bye', 'goodbye', 'see you']):
        return random.choice(["Goodbye! Feel free to come back anytime.", "Take care! Have a great day."])
    
    if user_input_lower in ['help', 'help me', 'what can you do']:
        return """I can help you with:
• Answering questions on any topic
• Finding information online
• Startup and business advice
• General knowledge questions

Just ask me anything!"""
    
    print(f"Searching for: {user_input}")
    search_results = search_engine.get_answer(user_input)
    
    if search_results:
        return f"{search_results}\n\nIs there anything specific you'd like to know more about?"
    else:
        return f"I understand you're asking about: {user_input}\n\nCould you provide a bit more detail so I can give you the best answer?"

# ============================================
# STIMULATOR MODULE
# ============================================

class MonteCarloSimulator:
    def __init__(self):
        self.results = {}
    
    def run_runway_simulation(self, current_burn_rate, current_cash, monthly_revenue, 
                              revenue_growth_range, expense_growth_range, iterations=1000):
        results = []
        for _ in range(iterations):
            revenue_growth = np.random.uniform(revenue_growth_range[0], revenue_growth_range[1])
            expense_growth = np.random.uniform(expense_growth_range[0], expense_growth_range[1])
            cash = current_cash
            months = 0
            revenue = monthly_revenue
            while cash > 0 and months < 36:
                monthly_expenses = current_burn_rate * (1 + expense_growth) ** (months / 12)
                revenue = revenue * (1 + revenue_growth / 100)
                net_cash_flow = revenue - monthly_expenses
                cash += net_cash_flow
                months += 1
                if cash <= 0:
                    break
            results.append(months)
        results = np.array(results)
        return {
            'p10_runway': np.percentile(results, 10),
            'p50_runway': np.percentile(results, 50),
            'p90_runway': np.percentile(results, 90),
            'survival_probability_12m': np.sum(results >= 12) / iterations * 100,
            'survival_probability_18m': np.sum(results >= 18) / iterations * 100,
            'distribution': results
        }

class StartupAnalyzer:
    def __init__(self):
        self.mc_simulator = MonteCarloSimulator()
    
    def generate_sample_data(self):
        np.random.seed(42)
        start_date = datetime(2024, 1, 1)
        months = [start_date + timedelta(days=30*i) for i in range(12)]
        data = {
            'Month': months,
            'Revenue': np.random.normal(50000, 15000, 12).cumsum(),
            'Users': np.random.normal(1000, 300, 12).cumsum(),
            'Customer_Acquisition_Cost': np.random.uniform(50, 150, 12),
            'Churn_Rate': np.random.uniform(2, 8, 12),
            'Net_Promoter_Score': np.random.uniform(30, 80, 12),
            'Burn_Rate': np.random.normal(30000, 8000, 12),
            'Monthly_Growth': np.random.uniform(-5, 25, 12)
        }
        df = pd.DataFrame(data)
        df['Revenue'] = df['Revenue'].clip(lower=0)
        df['Users'] = df['Users'].clip(lower=0)
        return df
    
    def calculate_startup_metrics(self, df):
        try:
            latest = df.iloc[-1]
            revenue_growth = ((df['Revenue'].iloc[-1] - df['Revenue'].iloc[0]) / df['Revenue'].iloc[0]) * 100 if df['Revenue'].iloc[0] > 0 else 0
            user_growth = ((df['Users'].iloc[-1] - df['Users'].iloc[0]) / df['Users'].iloc[0]) * 100 if df['Users'].iloc[0] > 0 else 0
            return {
                'revenue_growth': revenue_growth,
                'user_growth': user_growth,
                'avg_cac': df['Customer_Acquisition_Cost'].mean(),
                'avg_churn': df['Churn_Rate'].mean(),
                'avg_nps': df['Net_Promoter_Score'].mean(),
                'latest_revenue': latest['Revenue'],
                'latest_users': latest['Users'],
                'burn_rate': latest['Burn_Rate']
            }
        except Exception as e:
            return {}
    
    def analyze_startup_health(self, df):
        try:
            metrics = self.calculate_startup_metrics(df)
            health_score = 0
            if metrics.get('revenue_growth', 0) > 20: health_score += 25
            elif metrics.get('revenue_growth', 0) > 10: health_score += 15
            else: health_score += 5
            if metrics.get('user_growth', 0) > 20: health_score += 25
            elif metrics.get('user_growth', 0) > 10: health_score += 15
            else: health_score += 5
            if metrics.get('avg_cac', 100) < 80: health_score += 15
            elif metrics.get('avg_cac', 100) < 120: health_score += 10
            else: health_score += 5
            if metrics.get('avg_churn', 5) < 3: health_score += 15
            elif metrics.get('avg_churn', 5) < 5: health_score += 10
            else: health_score += 5
            if metrics.get('avg_nps', 40) > 60: health_score += 10
            elif metrics.get('avg_nps', 40) > 40: health_score += 5
            else: health_score += 0
            
            mc_runway = self.mc_simulator.run_runway_simulation(
                current_burn_rate=metrics.get('burn_rate', 30000),
                current_cash=metrics.get('burn_rate', 30000) * 12,
                monthly_revenue=metrics.get('latest_revenue', 50000),
                revenue_growth_range=(5, 25),
                expense_growth_range=(2, 10)
            )
            
            if health_score >= 80:
                status, color, recommendation = "Excellent", "#00ff00", f"Excellent! Monte Carlo shows {mc_runway.get('survival_probability_18m', 85):.0f}% survival at 18 months."
            elif health_score >= 60:
                status, color, recommendation = "Good", "#00ccff", f"Good performance. {mc_runway.get('survival_probability_12m', 70):.0f}% survival at 12 months."
            elif health_score >= 40:
                status, color, recommendation = "Moderate", "#ffaa00", "Room for improvement. Focus on reducing churn and CAC."
            elif health_score >= 20:
                status, color, recommendation = "Critical", "#ff6600", f"Immediate attention needed. P50 runway is {mc_runway.get('p50_runway', 6):.1f} months."
            else:
                status, color, recommendation = "At Risk", "#ff0000", "Urgent action required. Consider pivoting strategy."
            
            return {
                'health_score': health_score,
                'status': status,
                'color': color,
                'recommendation': recommendation,
                'metrics': {
                    'Revenue Growth': f"{metrics.get('revenue_growth', 0):.1f}%",
                    'User Growth': f"{metrics.get('user_growth', 0):.1f}%",
                    'Avg CAC': f"${metrics.get('avg_cac', 0):.0f}",
                    'Avg Churn': f"{metrics.get('avg_churn', 0):.1f}%",
                    'NPS': f"{metrics.get('avg_nps', 0):.0f}",
                    'Latest Revenue': f"${metrics.get('latest_revenue', 0):,.0f}",
                    'Latest Users': f"{metrics.get('latest_users', 0):,.0f}",
                    'Burn Rate': f"${metrics.get('burn_rate', 0):,.0f}/month"
                },
                'monte_carlo': {
                    'p10_runway': mc_runway.get('p10_runway', 0),
                    'p50_runway': mc_runway.get('p50_runway', 0),
                    'p90_runway': mc_runway.get('p90_runway', 0),
                    'survival_12m': mc_runway.get('survival_probability_12m', 0),
                    'survival_18m': mc_runway.get('survival_probability_18m', 0)
                }
            }
        except Exception as e:
            return {'health_score': 50, 'status': 'Error', 'color': '#ff6600', 'recommendation': str(e), 'metrics': {}, 'monte_carlo': {}}
    
    def generate_plots(self, df):
        plots = {}
        try:
            month_labels = [d.strftime('%b %Y') for d in df['Month']]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(range(len(df)), df['Revenue'], marker='o', linewidth=2, color='#00ffea')
            ax.fill_between(range(len(df)), 0, df['Revenue'], alpha=0.3, color='#00ffea')
            ax.set_title('Revenue Growth', fontsize=14, color='white')
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(month_labels, rotation=45)
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            img = io.BytesIO()
            fig.savefig(img, format='png', bbox_inches='tight', facecolor='none', dpi=100)
            img.seek(0)
            plots['revenue_chart'] = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)
        except Exception as e:
            print(f"Plot error: {e}")
        return plots

analyzer = StartupAnalyzer()

# ============================================
# HTML TEMPLATES
# ============================================

CHAT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Space Grotesk', sans-serif;
            background: radial-gradient(circle at 20% 30%, #0a0a2a, #010105);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            background: linear-gradient(135deg, #00ffea, #ff00e0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .chat-box {
            background: rgba(20, 30, 45, 0.4);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(0, 255, 255, 0.2);
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
        }
        .user-message { text-align: right; }
        .bot-message { text-align: left; }
        .message-content {
            display: inline-block;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 80%;
        }
        .user-message .message-content {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
        }
        .bot-message .message-content {
            background: rgba(30, 40, 60, 0.9);
            border-left: 3px solid #00ffea;
        }
        .chat-input-area {
            padding: 15px;
            border-top: 1px solid rgba(0, 255, 255, 0.2);
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 25px;
            padding: 12px 20px;
            color: white;
            font-family: inherit;
        }
        .send-btn {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border: none;
            border-radius: 25px;
            padding: 12px 25px;
            color: white;
            cursor: pointer;
        }
        .typing-indicator {
            padding: 10px 15px;
            background: rgba(30, 40, 60, 0.9);
            border-radius: 20px;
            display: inline-block;
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
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> AI Assistant</h1>
            <p>Ask me anything</p>
        </div>
        <div class="chat-box">
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <div class="message-content">Hello! I'm your AI assistant. What would you like to know?</div>
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="Type your message...">
                <button class="send-btn" id="sendBtn"><i class="fas fa-paper-plane"></i> Send</button>
            </div>
        </div>
    </div>
    <script>
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        
        function addMessage(message, isUser) {
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            div.innerHTML = `<div class="message-content">${message}</div>`;
            chatMessages.appendChild(div);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTyping() {
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.id = 'typing';
            div.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
            chatMessages.appendChild(div);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function removeTyping() {
            const typing = document.getElementById('typing');
            if (typing) typing.remove();
        }
        
        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            addMessage(message, true);
            chatInput.value = '';
            showTyping();
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                removeTyping();
                addMessage(data.response, false);
            } catch (error) {
                removeTyping();
                addMessage('Sorry, I had trouble connecting. Please try again.', false);
            }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
'''

STIMULATOR_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Startup Simulator</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Space Grotesk', sans-serif;
            background: radial-gradient(circle at 20% 30%, #0a0a2a, #010105);
            color: white;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { background: linear-gradient(135deg, #00ffea, #ff00e0); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .tabs { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; }
        .tab-btn {
            background: rgba(20, 30, 45, 0.6);
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 10px 25px;
            border-radius: 50px;
            cursor: pointer;
            color: white;
        }
        .tab-btn.active { background: linear-gradient(135deg, #00c6ff, #0072ff); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .card {
            background: rgba(20, 30, 45, 0.4);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(0, 255, 255, 0.2);
            padding: 20px;
            margin-bottom: 20px;
        }
        button {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            color: white;
            cursor: pointer;
        }
        .health-score { text-align: center; }
        .score-circle {
            width: 150px;
            height: 150px;
            margin: 20px auto;
            position: relative;
        }
        .score-value {
            font-size: 40px;
            font-weight: bold;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metric-card {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .metric-value { font-size: 24px; font-weight: bold; color: #00ffea; }
        .recommendation-box {
            background: rgba(0, 0, 0, 0.5);
            border-left: 4px solid #00ffea;
            padding: 15px;
            border-radius: 10px;
        }
        .mc-stats {
            display: flex;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .mc-stat-card {
            flex: 1;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .mc-stat-value { font-size: 20px; font-weight: bold; color: #ffaa00; }
        .loading { text-align: center; padding: 40px; }
        .loading i { font-size: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        input {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 10px;
            padding: 10px;
            color: white;
            width: 100%;
        }
        .grid-2col { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        @media (max-width: 768px) { .grid-2col { grid-template-columns: 1fr; } }
        .file-upload {
            border: 2px dashed rgba(0, 255, 255, 0.5);
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
        }
        .chart-container img { width: 100%; border-radius: 10px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> Startup Performance Simulator</h1>
            <p>Monte Carlo Analytics | Risk-Aware Decision Making</p>
        </div>
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('sample')">Sample Data</button>
            <button class="tab-btn" onclick="switchTab('manual')">Manual Entry</button>
        </div>
        <div id="sample-tab" class="tab-content active">
            <div class="card">
                <button onclick="loadSampleData()" style="width: 100%;"><i class="fas fa-play"></i> Load Sample Data & Run Simulations</button>
            </div>
        </div>
        <div id="manual-tab" class="tab-content">
            <div class="card">
                <div class="grid-2col">
                    <input type="number" id="revenue" placeholder="Monthly Revenue ($)" value="50000">
                    <input type="number" id="users" placeholder="Total Users" value="1000">
                    <input type="number" id="cac" placeholder="Customer Acquisition Cost ($)" value="75">
                    <input type="number" id="churn" placeholder="Churn Rate (%)" value="5">
                    <input type="number" id="nps" placeholder="Net Promoter Score" value="60">
                    <input type="number" id="growth" placeholder="Growth Rate (%)" value="15">
                    <input type="number" id="burn" placeholder="Burn Rate ($/month)" value="30000">
                </div>
                <button onclick="analyzeManual()" style="width: 100%; margin-top: 15px;">Analyze with Monte Carlo</button>
            </div>
        </div>
        <div id="results" style="display: none;"></div>
    </div>
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tab + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const health = data.health;
            const mc = health.monte_carlo;
            
            let metricsHtml = '<div class="metrics-grid">';
            for (const [key, value] of Object.entries(health.metrics)) {
                metricsHtml += `<div class="metric-card"><div class="metric-value">${value}</div><div class="metric-label">${key}</div></div>`;
            }
            metricsHtml += '</div>';
            
            let mcHtml = '<div class="mc-stats">';
            mcHtml += `<div class="mc-stat-card"><div class="mc-stat-value">${mc.p50_runway?.toFixed(1) || 'N/A'} mo</div><div>Median Runway</div></div>`;
            mcHtml += `<div class="mc-stat-card"><div class="mc-stat-value">${mc.survival_12m?.toFixed(1) || 'N/A'}%</div><div>Survival 12mo</div></div>`;
            mcHtml += `<div class="mc-stat-card"><div class="mc-stat-value">${mc.survival_18m?.toFixed(1) || 'N/A'}%</div><div>Survival 18mo</div></div>`;
            mcHtml += '</div>';
            
            resultsDiv.innerHTML = `
                <div class="card">
                    <div class="health-score">
                        <div class="score-circle">
                            <canvas id="healthCanvas" width="150" height="150"></canvas>
                            <div class="score-value">${health.health_score}</div>
                        </div>
                        <div class="status-badge" style="background: ${health.color}20; border: 1px solid ${health.color}; display: inline-block; padding: 5px 15px; border-radius: 50px;">${health.status}</div>
                    </div>
                    ${metricsHtml}
                    ${mcHtml}
                    <div class="recommendation-box"><strong>Recommendation:</strong> ${health.recommendation}</div>
                </div>
            `;
            
            setTimeout(() => {
                const canvas = document.getElementById('healthCanvas');
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    const angle = (health.health_score / 100) * Math.PI * 2;
                    ctx.clearRect(0, 0, 150, 150);
                    ctx.beginPath();
                    ctx.arc(75, 75, 65, 0, Math.PI * 2);
                    ctx.strokeStyle = '#333';
                    ctx.lineWidth = 12;
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(75, 75, 65, -Math.PI/2, angle - Math.PI/2);
                    ctx.strokeStyle = health.color;
                    ctx.lineWidth = 12;
                    ctx.stroke();
                }
            }, 100);
            
            if (data.charts && data.charts.revenue_chart) {
                resultsDiv.innerHTML += `<div class="card"><div class="chart-container"><img src="data:image/png;base64,${data.charts.revenue_chart}"></div></div>`;
            }
            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function loadSampleData() {
            document.getElementById('results').style.display = 'block';
            document.getElementById('results').innerHTML = '<div class="card loading"><i class="fas fa-spinner fa-pulse"></i> Running Monte Carlo simulations...</div>';
            const response = await fetch('/api/generate_sample');
            const data = await response.json();
            if (data.success) displayResults(data);
            else document.getElementById('results').innerHTML = `<div class="card">Error: ${data.error}</div>`;
        }
        
        async function analyzeManual() {
            const data = {
                revenue: document.getElementById('revenue').value,
                users: document.getElementById('users').value,
                cac: document.getElementById('cac').value,
                churn: document.getElementById('churn').value,
                nps: document.getElementById('nps').value,
                growth: document.getElementById('growth').value,
                burn: document.getElementById('burn').value
            };
            document.getElementById('results').style.display = 'block';
            document.getElementById('results').innerHTML = '<div class="card loading"><i class="fas fa-spinner fa-pulse"></i> Running simulations...</div>';
            const response = await fetch('/api/analyze_manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) displayResults(result);
            else document.getElementById('results').innerHTML = `<div class="card">Error: ${result.error}</div>`;
        }
    </script>
</body>
</html>
'''

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return send_file('dashboard.html')

@app.route('/chat')
def chat():
    return render_template_string(CHAT_HTML)

@app.route('/stimulator')
def stimulator():
    return render_template_string(STIMULATOR_HTML)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    response = get_response(data.get('message', ''))
    return jsonify({'response': response})

@app.route('/api/generate_sample', methods=['GET'])
def generate_sample():
    try:
        df = analyzer.generate_sample_data()
        health = analyzer.analyze_startup_health(df)
        plots = analyzer.generate_plots(df)
        return jsonify({'success': True, 'health': health, 'charts': plots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze_manual', methods=['POST'])
def analyze_manual():
    try:
        data = request.json
        start_date = datetime(2024, 1, 1)
        months = [start_date + timedelta(days=30*i) for i in range(6)]
        revenue = float(data.get('revenue', 50000))
        users = float(data.get('users', 1000))
        cac = float(data.get('cac', 75))
        churn = float(data.get('churn', 5))
        nps = float(data.get('nps', 60))
        growth = float(data.get('growth', 15))
        burn = float(data.get('burn', 30000))
        
        df_data = []
        for i in range(6):
            df_data.append({
                'Month': months[i],
                'Revenue': revenue * (1 + growth/100) ** i,
                'Users': users * (1 + growth/100) ** i,
                'Customer_Acquisition_Cost': max(10, cac * (1 - 0.05 * i)),
                'Churn_Rate': max(1, churn * (1 - 0.03 * i)),
                'Net_Promoter_Score': min(100, nps + i * 2),
                'Burn_Rate': burn * (1 + 0.05 * i),
                'Monthly_Growth': growth
            })
        df = pd.DataFrame(df_data)
        health = analyzer.analyze_startup_health(df)
        plots = analyzer.generate_plots(df)
        return jsonify({'success': True, 'health': health, 'charts': plots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🚀 AI VentureForge - Fully Combined App              ║
    ║                                                          ║
    ║  Server running at: http://localhost:5000                ║
    ║                                                          ║
    ║  Routes:                                                 ║
    ║  • /          - Main Dashboard                           ║
    ║  • /chat      - AI Assistant Chatbot                     ║
    ║  • /stimulator - Startup Performance Simulator           ║
    ║                                                          ║
    ║  Both chat button AND stimulator tab work!               ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)