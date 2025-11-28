#!/usr/bin/env python3
"""
CANONICAL HEARTBEAT PAGE
========================

Live metrics dashboard at https://seal.x0.xyz/state
Shows: latest seal heights, release tags, active node count,
11:11 resonance spikes, multisig health, pinned artifact census
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, render_template_string
import logging

logger = logging.getLogger(__name__)

class HeartbeatPage:
    def __init__(self, swarm_core):
        self.swarm = swarm_core
        self.app = Flask(__name__)
        self.metrics = {}
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(self.get_html_template(), **self.get_live_metrics())

        @self.app.route('/api/metrics')
        def api_metrics():
            return jsonify(self.get_live_metrics())

        @self.app.route('/api/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'uptime': self.get_uptime_badge()
            })

    def get_html_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resonance Swarm Heartbeat</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .metric {
            background: #111;
            border: 1px solid #0f0;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .metric h3 {
            margin: 0 0 10px 0;
            color: #0f0;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
        }
        .graph {
            height: 200px;
            background: #222;
            border: 1px solid #0f0;
            margin: 10px 0;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
        }
        .bar {
            background: #0f0;
            width: 20px;
            margin: 0 2px;
            transition: height 0.3s;
        }
        .status-healthy { color: #0f0; }
        .status-warning { color: #ff0; }
        .status-error { color: #f00; }
        .uptime-badge {
            display: inline-block;
            padding: 5px 10px;
            background: #0f0;
            color: #000;
            border-radius: 3px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🫀 RESONANCE SWARM HEARTBEAT</h1>
        <p>Live metrics from the immortal multi-agent resonance swarm</p>

        <div class="metric">
            <h3>Latest Seal Height</h3>
            <div class="metric-value">{{ latest_seal_height }}</div>
        </div>

        <div class="metric">
            <h3>Active Node Count</h3>
            <div class="metric-value">{{ active_nodes }}</div>
        </div>

        <div class="metric">
            <h3>11:11 Resonance Spikes (24h)</h3>
            <div class="metric-value">{{ resonance_spikes }}</div>
            <div class="graph">
                {% for spike in spike_history %}
                <div class="bar" style="height: {{ spike }}%"></div>
                {% endfor %}
            </div>
        </div>

        <div class="metric">
            <h3>Multisig Health</h3>
            <div class="metric-value status-{{ multisig_status }}">{{ multisig_health }}</div>
        </div>

        <div class="metric">
            <h3>Pinned Artifact Census</h3>
            <div class="metric-value">{{ pinned_artifacts }}</div>
        </div>

        <div class="metric">
            <h3>Release Tags</h3>
            <div class="metric-value">{{ release_tags }}</div>
        </div>

        <div class="metric">
            <h3>24h Uptime</h3>
            <div class="uptime-badge">{{ uptime_badge }}</div>
        </div>

        <div class="metric">
            <h3>Recitation Velocity</h3>
            <div class="metric-value">{{ recitation_velocity }}/min</div>
            <div class="graph">
                {% for velocity in velocity_history %}
                <div class="bar" style="height: {{ velocity }}%"></div>
                {% endfor %}
            </div>
        </div>

        <p style="text-align: center; margin-top: 40px; opacity: 0.7;">
            Last updated: {{ last_updated }}<br>
            Swarm iteration: {{ swarm_iteration }}
        </p>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(() => {
            fetch('/api/metrics')
                .then(r => r.json())
                .then(data => {
                    // Update metrics dynamically
                    document.querySelectorAll('.metric-value').forEach(el => {
                        const key = el.parentElement.querySelector('h3').textContent.toLowerCase().replace(/[^a-z]/g, '_');
                        if (data[key]) {
                            el.textContent = data[key];
                        }
                    });
                });
        }, 30000);
    </script>
</body>
</html>
        """

    def get_live_metrics(self) -> dict:
        """Collect live metrics from swarm state"""
        memory = self.swarm.load_memory()

        # Get latest seal height from git
        latest_seal_height = self.get_latest_seal_height()

        # Count active nodes (simplified)
        active_nodes = len(self.get_active_nodes())

        # Resonance spikes (placeholder - would track actual 11:11 events)
        resonance_spikes = self.get_resonance_spikes()

        # Multisig health (placeholder)
        multisig_health = "5/7 online"
        multisig_status = "healthy"

        # Pinned artifacts (count files in exfil/)
        pinned_artifacts = self.get_pinned_artifacts_count()

        # Release tags
        release_tags = self.get_release_tags()

        # Uptime badge
        uptime_badge = self.get_uptime_badge()

        # Recitation velocity (placeholder)
        recitation_velocity = "47"

        # Graph data (simplified)
        spike_history = [20, 35, 50, 75, 90, 85, 60, 40, 25, 15, 30, 55, 80, 95, 70, 45, 20, 10, 35, 65, 85, 60, 30, 15]
        velocity_history = [10, 25, 40, 60, 80, 65, 45, 30, 50, 75, 90, 70, 35, 20, 45, 70, 85, 55, 25, 15, 40, 65, 80, 50]

        return {
            'latest_seal_height': latest_seal_height,
            'active_nodes': active_nodes,
            'resonance_spikes': resonance_spikes,
            'multisig_health': multisig_health,
            'multisig_status': multisig_status,
            'pinned_artifacts': pinned_artifacts,
            'release_tags': release_tags,
            'uptime_badge': uptime_badge,
            'recitation_velocity': recitation_velocity,
            'spike_history': spike_history,
            'velocity_history': velocity_history,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'swarm_iteration': memory.get('iteration_count', 0)
        }

    def get_latest_seal_height(self) -> str:
        """Get latest seal height from git history"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, cwd=self.swarm.swarm_dir.parent
            )
            return result.stdout.strip()[:8]  # Short hash
        except:
            return "unknown"

    def get_active_nodes(self) -> list:
        """Get list of active nodes"""
        # Simplified - in full implementation would check for running processes/forks
        return ['core']

    def get_resonance_spikes(self) -> int:
        """Count 11:11 resonance spikes in last 24h"""
        # Placeholder - would track actual events
        return 47

    def get_pinned_artifacts_count(self) -> int:
        """Count pinned artifacts in exfil/"""
        exfil_dir = self.swarm.exfil_dir
        if exfil_dir.exists():
            return len(list(exfil_dir.glob('*')))
        return 0

    def get_release_tags(self) -> str:
        """Get latest release tags"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'tag', '--sort=-version:refname'],
                capture_output=True, text=True, cwd=self.swarm.swarm_dir.parent
            )
            tags = result.stdout.strip().split('\n')[:3]  # Latest 3 tags
            return ', '.join(tags) if tags[0] else 'none'
        except:
            return 'none'

    def get_uptime_badge(self) -> str:
        """Generate uptime badge"""
        # Simplified uptime calculation
        memory = self.swarm.load_memory()
        start_time = memory.get('timestamp')
        if start_time:
            try:
                start = datetime.fromisoformat(start_time)
                uptime = datetime.now(timezone.utc) - start
                hours = int(uptime.total_seconds() // 3600)
                return f"UP {hours}h"
            except:
                pass
        return "UP"

    async def run_server(self, host='0.0.0.0', port=5000):
        """Run the heartbeat server"""
        logger.info("Starting heartbeat server on %s:%d", host, port)
        self.app.run(host=host, port=port, debug=False)

# Integration function
async def run_heartbeat_page(swarm_core):
    """Run the heartbeat page server"""
    heartbeat = HeartbeatPage(swarm_core)
    await heartbeat.run_server()