from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

ESP_IP = "10.29.228.88" 
ESP_URL = f"http://{ESP_IP}/data"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Yarana IoT Power Monitor</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f172a 100%);
      color: #e2e8f0;
      font-family: 'Inter', 'Segoe UI', sans-serif;
      min-height: 100vh;
      padding: 20px;
      overflow-x: hidden;
    }
    .header { text-align: center; padding: 20px 0 30px; position: relative; }
    .header h1 {
      font-size: clamp(1.8rem, 5vw, 3rem);
      background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
      font-weight: 800;
      letter-spacing: -1px;
    }
    .brand { display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap; }
    .brand-item {
      background: rgba(96, 165, 250, 0.1);
      padding: 8px 20px;
      border-radius: 20px;
      border: 1px solid rgba(96, 165, 250, 0.3);
      font-size: 0.9rem;
      color: #60a5fa;
      backdrop-filter: blur(10px);
    }
    .status {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(34, 197, 94, 0.15);
      padding: 8px 16px; border-radius: 20px;
      border: 1px solid rgba(34, 197, 94, 0.3);
      font-size: 0.85rem; margin-top: 15px;
    }
    .status-dot {
      width: 8px; height: 8px; background: #22c55e;
      border-radius: 50%; animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; box-shadow: 0 0 8px #22c55e; }
      50% { opacity: 0.5; box-shadow: 0 0 4px #22c55e; }
    }
    .container { max-width: 1400px; margin: 0 auto; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .card {
      background: rgba(30, 41, 59, 0.6);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 20px; padding: 25px;
      position: relative; overflow: hidden; transition: all 0.3s ease;
    }
    .card:hover { transform: translateY(-5px); border-color: rgba(96, 165, 250, 0.5); box-shadow: 0 20px 40px rgba(96, 165, 250, 0.2); }
    .card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #60a5fa, #a78bfa); }
    .card-icon { font-size: 2rem; margin-bottom: 10px; display: block; }
    .card-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .card-value { font-size: 2.5rem; font-weight: 700; color: #f1f5f9; margin-bottom: 5px; font-variant-numeric: tabular-nums; }
    .card-unit { font-size: 1.2rem; color: #60a5fa; font-weight: 500; }
    .chart-container {
      background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(20px);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }
    .chart-title { font-size: 1.3rem; color: #f1f5f9; margin-bottom: 20px; font-weight: 600; }
    canvas { max-height: 300px; }
    .footer { text-align: center; padding: 30px 20px; border-top: 1px solid rgba(148, 163, 184, 0.1); margin-top: 40px; }
    .footer-text { color: #64748b; font-size: 0.9rem; margin-bottom: 10px; }
    .creator { color: #60a5fa; font-weight: 600; font-size: 1rem; }
  </style>
</head>
<body>
  <div class="header">
    <h1>⚡ Real-Time Power Monitor</h1>
    <div class="brand">
      <div class="brand-item">📺 Power Monitoring Systeme</div>
      <div class="brand-item">🚀 IoT Dashboard </div>
    </div>
    <div class="status">
      <span class="status-dot"></span>
      <span id="wsStatus">Connecting...</span>
    </div>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card">
        <span class="card-icon">⚡</span>
        <div class="card-label">Voltage</div>
        <div class="card-value" id="voltage">--</div>
        <span class="card-unit">Volts</span>
      </div>
      <div class="card">
        <span class="card-icon">🔌</span>
        <div class="card-label">Current</div>
        <div class="card-value" id="current">--</div>
        <span class="card-unit">Ampere</span>
      </div>
      <div class="card">
        <span class="card-icon">💡</span>
        <div class="card-label">Power</div>
        <div class="card-value" id="power">--</div>
        <span class="card-unit">Watts</span>
      </div>
      <div class="card">
        <span class="card-icon">⚙️</span>
        <div class="card-label">Energy</div>
        <div class="card-value" id="energy">--</div>
        <span class="card-unit">kWh</span>
      </div>
      <div class="card">
        <span class="card-icon">📊</span>
        <div class="card-label">Frequency</div>
        <div class="card-value" id="frequency">--</div>
        <span class="card-unit">Hz</span>
      </div>
      <div class="card">
        <span class="card-icon">🎯</span>
        <div class="card-label">Power Factor</div>
        <div class="card-value" id="pf">--</div>
        <span class="card-unit">PF</span>
      </div>
    </div>
    <div class="chart-container">
      <div class="chart-title">📈 Power & Current Trends</div>
      <canvas id="powerChart"></canvas>
    </div>
    <div class="chart-container">
      <div class="chart-title">⚡ Voltage & Frequency Monitor</div>
      <canvas id="voltageChart"></canvas>
    </div>
  </div>
  <div class="footer">
    <div class="footer-text">Powered by ESP32 & PZEM-004T</div>
    <div class="creator">Created by mohamed benfaiza & aourane younes | students from USTHB </div>
    <div class="footer-text" style="margin-top: 10px;">© 2025 FACULITY OF ELECTRICAL ENGINEERING</div>
  </div>

  <script>
    const espIp = "{{esp_ip}}";
    let ws;
    const maxDataPoints = 20;
    let timeLabels = [], powerData = [], currentData = [], voltageData = [], frequencyData = [];

    // --- CHART INITIALIZATION ---
    const powerCtx = document.getElementById('powerChart').getContext('2d');
    const powerChart = new Chart(powerCtx, {
      type: 'line',
      data: {
        labels: timeLabels,
        datasets: [
          { label: 'Power (W)', data: powerData, borderColor: '#60a5fa', backgroundColor: 'rgba(96, 165, 250, 0.1)', tension: 0.4, fill: true, borderWidth: 2 },
          { label: 'Current (A)', data: currentData, borderColor: '#a78bfa', backgroundColor: 'rgba(167, 139, 250, 0.1)', tension: 0.4, fill: true, borderWidth: 2, yAxisID: 'y1' }
        ]
      },
      options: { responsive: true, plugins: { legend: { labels: { color: '#e2e8f0' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } }, y1: { position: 'right', ticks: { color: '#94a3b8' } } } }
    });

    const voltageCtx = document.getElementById('voltageChart').getContext('2d');
    const voltageChart = new Chart(voltageCtx, {
      type: 'line',
      data: {
        labels: timeLabels,
        datasets: [
          { label: 'Voltage (V)', data: voltageData, borderColor: '#f472b6', backgroundColor: 'rgba(244, 114, 182, 0.1)', tension: 0.4, fill: true, borderWidth: 2 },
          { label: 'Frequency (Hz)', data: frequencyData, borderColor: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.1)', tension: 0.4, fill: true, borderWidth: 2, yAxisID: 'y1' }
        ]
      },
      options: { responsive: true, plugins: { legend: { labels: { color: '#e2e8f0' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } }, y1: { position: 'right', ticks: { color: '#94a3b8' } } } }
    });

    // --- WEBSOCKET CONNECTION ---
    function connectWebSocket() {
      ws = new WebSocket(`ws://${espIp}:81`);
      
      ws.onopen = () => { document.getElementById('wsStatus').textContent = 'Connected'; };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateDisplay(data);
        updateCharts(data);
      };
      
      ws.onclose = () => {
        document.getElementById('wsStatus').textContent = 'Disconnected - Retrying...';
        setTimeout(connectWebSocket, 3000);
      };
    }

    function updateDisplay(data) {
      document.getElementById('voltage').textContent = data.voltage.toFixed(2);
      document.getElementById('current').textContent = data.current.toFixed(3);
      document.getElementById('power').textContent = data.power.toFixed(2);
      document.getElementById('energy').textContent = data.energy.toFixed(3);
      document.getElementById('frequency').textContent = data.frequency.toFixed(2);
      document.getElementById('pf').textContent = data.pf.toFixed(2);
    }

    function updateCharts(data) {
      const now = new Date();
      const timeStr = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
      
      if (timeLabels.length >= maxDataPoints) {
        timeLabels.shift(); powerData.shift(); currentData.shift(); voltageData.shift(); frequencyData.shift();
      }
      
      timeLabels.push(timeStr);
      powerData.push(data.power);
      currentData.push(data.current);
      voltageData.push(data.voltage);
      frequencyData.push(data.frequency);
      
      powerChart.update('none');
      voltageChart.update('none');
    }

    connectWebSocket();
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, esp_ip=ESP_IP)

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=True)