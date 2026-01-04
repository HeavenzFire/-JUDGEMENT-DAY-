#!/usr/bin/env python3
"""
Unified System Dashboard
Web-based dashboard for monitoring and controlling all connected systems.
"""

import logging
import json
import time
from flask import Flask, render_template_string, request, jsonify
from master_orchestrator import orchestrator
from cross_system_communication import communication_hub, MessageType, SystemMessage
from system_integration_layer import integration_layer

logger = logging.getLogger(__name__)

class UnifiedDashboard:
    """Unified dashboard for all systems."""

    def __init__(self, host='0.0.0.0', port=8080):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template_string(self.get_dashboard_html())

        @self.app.route('/api/systems/status')
        def get_system_status():
            """Get status of all systems."""
            status = orchestrator.get_system_status()
            return jsonify(status)

        @self.app.route('/api/systems/info')
        def get_system_info():
            """Get detailed system information."""
            info = orchestrator.get_system_info()
            return jsonify(info)

        @self.app.route('/api/mesh/status')
        def get_mesh_status():
            """Get mesh status."""
            status = integration_layer.get_mesh_status()
            return jsonify(status)

        @self.app.route('/api/messages/history')
        def get_message_history():
            """Get message history."""
            history = communication_hub.get_message_history(limit=50)
            history_data = [msg.to_dict() for msg in history]
            return jsonify(history_data)

        @self.app.route('/api/systems/<system_name>/control', methods=['POST'])
        def control_system(system_name):
            """Control a specific system."""
            action = request.json.get('action')
            result = False

            if action == 'start':
                result = orchestrator.start_system(system_name)
            elif action == 'stop':
                result = orchestrator.stop_system(system_name)
            elif action == 'restart':
                orchestrator.stop_system(system_name)
                time.sleep(1)
                result = orchestrator.start_system(system_name)

            return jsonify({'success': result, 'action': action, 'system': system_name})

        @self.app.route('/api/messages/send', methods=['POST'])
        def send_message():
            """Send a message between systems."""
            data = request.json
            message = SystemMessage(
                message_id=f"dashboard_{int(time.time())}",
                from_system="dashboard",
                to_system=data['to_system'],
                message_type=MessageType(data['message_type']),
                payload=data['payload'],
                timestamp=time.time()
            )

            success = communication_hub.send_message(message)
            return jsonify({'success': success, 'message_id': message.message_id})

    def get_dashboard_html(self) -> str:
        """Get the dashboard HTML template."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified System Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .system-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .system-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-running { background-color: #27ae60; }
        .status-stopped { background-color: #e74c3c; }
        .status-initialized { background-color: #f39c12; }
        .status-failed { background-color: #e74c3c; }
        .control-btn { background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 5px; }
        .control-btn:hover { background: #2980b9; }
        .message-list { max-height: 400px; overflow-y: auto; background: white; border-radius: 8px; padding: 10px; }
        .message-item { padding: 8px; border-bottom: 1px solid #eee; font-size: 12px; }
        .chart-container { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 Unified System Dashboard</h1>
            <p>Monitoring and controlling all connected systems</p>
        </div>

        <div class="chart-container">
            <h2>System Status Overview</h2>
            <canvas id="statusChart" width="400" height="200"></canvas>
        </div>

        <div class="system-grid" id="systemGrid">
            <!-- System cards will be populated by JavaScript -->
        </div>

        <div class="chart-container">
            <h2>Message History</h2>
            <div class="message-list" id="messageList">
                <!-- Messages will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        let statusChart;

        async function updateDashboard() {
            try {
                // Update system status
                const statusResponse = await fetch('/api/systems/status');
                const statusData = await statusResponse.json();

                // Update system info
                const infoResponse = await fetch('/api/systems/info');
                const infoData = await infoResponse.json();

                // Update mesh status
                const meshResponse = await fetch('/api/mesh/status');
                const meshData = await meshResponse.json();

                updateSystemGrid(statusData, infoData);
                updateStatusChart(statusData);
                updateMessageHistory();

                document.querySelector('.header p').textContent =
                    `Monitoring ${meshData.total_systems} systems - Mesh Status: ${meshData.communication_status}`;

            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }

        function updateSystemGrid(statusData, infoData) {
            const grid = document.getElementById('systemGrid');
            grid.innerHTML = '';

            for (const [systemName, status] of Object.entries(statusData)) {
                const info = infoData[systemName] || {};
                const card = createSystemCard(systemName, status, info);
                grid.appendChild(card);
            }
        }

        function createSystemCard(systemName, status, info) {
            const card = document.createElement('div');
            card.className = 'system-card';

            const statusClass = `status-${status}`;
            const capabilities = info.capabilities || [];

            card.innerHTML = `
                <h3>
                    <span class="status-indicator ${statusClass}"></span>
                    ${systemName}
                </h3>
                <p><strong>Status:</strong> ${status}</p>
                <p><strong>Capabilities:</strong> ${capabilities.join(', ') || 'None'}</p>
                <div>
                    <button class="control-btn" onclick="controlSystem('${systemName}', 'start')">Start</button>
                    <button class="control-btn" onclick="controlSystem('${systemName}', 'stop')">Stop</button>
                    <button class="control-btn" onclick="controlSystem('${systemName}', 'restart')">Restart</button>
                </div>
            `;

            return card;
        }

        async function controlSystem(systemName, action) {
            try {
                const response = await fetch(`/api/systems/${systemName}/control`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action })
                });
                const result = await response.json();
                alert(`${action} ${systemName}: ${result.success ? 'Success' : 'Failed'}`);
                updateDashboard();
            } catch (error) {
                console.error('Error controlling system:', error);
            }
        }

        function updateStatusChart(statusData) {
            const ctx = document.getElementById('statusChart').getContext('2d');

            const statusCounts = {};
            for (const status of Object.values(statusData)) {
                statusCounts[status] = (statusCounts[status] || 0) + 1;
            }

            const data = {
                labels: Object.keys(statusCounts),
                datasets: [{
                    label: 'System Status',
                    data: Object.values(statusCounts),
                    backgroundColor: [
                        '#27ae60', // running
                        '#e74c3c', // stopped
                        '#f39c12', // initialized
                        '#95a5a6'  // failed
                    ]
                }]
            };

            if (statusChart) {
                statusChart.data = data;
                statusChart.update();
            } else {
                statusChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: data,
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
        }

        async function updateMessageHistory() {
            try {
                const response = await fetch('/api/messages/history');
                const messages = await response.json();

                const list = document.getElementById('messageList');
                list.innerHTML = '';

                messages.reverse().forEach(msg => {
                    const item = document.createElement('div');
                    item.className = 'message-item';
                    item.innerHTML = `
                        <strong>${msg.from_system} → ${msg.to_system}</strong>
                        <span style="color: #666;">[${msg.message_type}]</span>
                        <div style="font-size: 11px; color: #888;">
                            ${new Date(msg.timestamp * 1000).toLocaleTimeString()}
                        </div>
                    `;
                    list.appendChild(item);
                });
            } catch (error) {
                console.error('Error updating message history:', error);
            }
        }

        // Update dashboard every 5 seconds
        setInterval(updateDashboard, 5000);

        // Initial load
        updateDashboard();
    </script>
</body>
</html>
        """

    def start(self):
        """Start the dashboard server."""
        logger.info(f"Starting unified dashboard on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)

    def stop(self):
        """Stop the dashboard server."""
        # Flask doesn't have a direct stop method, but we can use a flag
        pass

# Global dashboard instance
dashboard = UnifiedDashboard()

if __name__ == "__main__":
    dashboard.start()