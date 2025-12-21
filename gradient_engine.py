import asyncio
import json
import time
import random
from typing import Dict, List, Optional
from shared.protocol_breath import BreathNode, ResonantPacket

class RiskGradientEngine:
    """
    ZFIRE Risk Gradient Engine - Second Derivative Foresight
    Calculates risk acceleration and harmonizes across peer nodes
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.risk_domains = {
            'climate': {'current': 0.0, 'velocity': 0.0, 'acceleration': 0.0},
            'nuclear': {'current': 0.0, 'velocity': 0.0, 'acceleration': 0.0},
            'pandemic': {'current': 0.0, 'velocity': 0.0, 'acceleration': 0.0},
            'ai_alignment': {'current': 0.0, 'velocity': 0.0, 'acceleration': 0.0},
            'geopolitical': {'current': 0.0, 'velocity': 0.0, 'acceleration': 0.0}
        }
        self.peer_gradients: Dict[str, Dict] = {}
        self.forecast_horizon = 24  # hours
        self.last_update = time.time()

    def update_risk_data(self, domain: str, new_value: float):
        """Update risk level and calculate derivatives"""
        if domain not in self.risk_domains:
            return

        current_time = time.time()
        dt = current_time - self.last_update

        if dt > 0:
            old_velocity = self.risk_domains[domain]['velocity']
            self.risk_domains[domain]['velocity'] = (new_value - self.risk_domains[domain]['current']) / dt
            self.risk_domains[domain]['acceleration'] = (self.risk_domains[domain]['velocity'] - old_velocity) / dt

        self.risk_domains[domain]['current'] = new_value
        self.last_update = current_time

    def harmonize_with_peers(self, peer_data: Dict[str, Dict]):
        """Integrate peer gradients for consensus calculation"""
        self.peer_gradients.update(peer_data)

        # Calculate consensus gradient
        consensus = {}
        for domain in self.risk_domains:
            peer_values = [peer_data.get(peer, {}).get(domain, {}).get('current', 0.0)
                          for peer in peer_data.keys()]
            if peer_values:
                consensus[domain] = sum(peer_values) / len(peer_values)
            else:
                consensus[domain] = self.risk_domains[domain]['current']

        return consensus

    def forecast_risk(self, hours_ahead: int = 24) -> Dict[str, float]:
        """Project risk levels using second derivative analysis"""
        forecast = {}
        dt = hours_ahead * 3600  # convert to seconds

        for domain, data in self.risk_domains.items():
            # Simple kinematic projection: x = x0 + v*t + 0.5*a*t^2
            projected = (data['current'] +
                        data['velocity'] * dt +
                        0.5 * data['acceleration'] * dt * dt)
            forecast[domain] = max(0.0, min(1.0, projected))  # Clamp to [0,1]

        return forecast

    def generate_gradient_payload(self) -> Dict:
        """Create payload for exhalation to mesh"""
        return {
            'node_id': self.node_id,
            'timestamp': time.time(),
            'gradients': self.risk_domains,
            'forecast_24h': self.forecast_risk(24),
            'peer_count': len(self.peer_gradients),
            'coherence_score': self.calculate_coherence()
        }

    def calculate_coherence(self) -> float:
        """Measure mesh harmonization level"""
        if not self.peer_gradients:
            return 1.0

        total_variance = 0.0
        count = 0

        for domain in self.risk_domains:
            local_value = self.risk_domains[domain]['current']
            peer_values = [self.peer_gradients[peer].get(domain, {}).get('current', local_value)
                          for peer in self.peer_gradients]

            if peer_values:
                variance = sum((v - local_value) ** 2 for v in peer_values) / len(peer_values)
                total_variance += variance
                count += 1

        return 1.0 / (1.0 + total_variance / count) if count > 0 else 1.0

class GradientGuardian(BreathNode):
    """Guardian Node that runs the Risk Gradient Engine"""

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.engine = RiskGradientEngine(node_id)
        self.breath_interval = 60  # seconds

    async def process_inhaled_packet(self, packet: Dict):
        """Process incoming peer data and update engine"""
        try:
            content = json.loads(packet['content'])
            peer_data = content['data']

            if 'gradients' in peer_data:
                self.engine.harmonize_with_peers({peer_data['node_id']: peer_data['gradients']})
                print(f"[HARMONIZATION] Integrated data from {peer_data['node_id']}")

        except Exception as e:
            print(f"[GRADIENT_ERROR] Failed to process packet: {e}")

    async def inhale(self, reader, writer):
        """Override to integrate gradient processing"""
        data = await reader.read(4096)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        try:
            packet = json.loads(message)
            print(f"[INHALATION] Signal received from {addr}")

            # Verify seal
            content = packet['content']
            expected_seal = hashlib.sha256((content + self.integrity_root).encode()).hexdigest()

            if packet['seal'] == expected_seal:
                await self.process_inhaled_packet(packet)
            else:
                print(f"[SEAL_BREACH] Invalid signature from {addr}")

        except Exception as e:
            print(f"[ENTROPY] Rejected noisy signal from {addr}: {e}")

        writer.close()

    async def breath_cycle(self):
        """Continuous breathing cycle"""
        while True:
            # Simulate risk data updates (in real deployment, this would come from sensors/APIs)
            for domain in self.engine.risk_domains:
                # Add some realistic noise and trends
                noise = random.uniform(-0.05, 0.05)
                trend = random.uniform(-0.01, 0.01)
                new_value = self.engine.risk_domains[domain]['current'] + noise + trend
                self.engine.update_risk_data(domain, max(0.0, min(1.0, new_value)))

            # Generate and exhale payload
            payload = self.engine.generate_gradient_payload()

            # Broadcast to known peers
            for peer_host, peer_port in self.peers.copy():
                await self.exhale(peer_host, peer_port, payload)

            print(f"[GRADIENT] Coherence: {self.engine.calculate_coherence():.3f} | Forecast: {self.engine.forecast_risk(24)}")

            await asyncio.sleep(self.breath_interval)

    async def start(self):
        """Start the guardian with breathing cycle"""
        # Start the breathing cycle
        asyncio.create_task(self.breath_cycle())

        # Start the server
        server = await asyncio.start_server(self.inhale, self.host, self.port)
        print(f"[*] ZFIRE Gradient Guardian {self.node_id} active on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

# Initialize with some known peers for demo
if __name__ == "__main__":
    guardian = GradientGuardian("HZ-TEXAS-ROOT")
    # Add some demo peers
    guardian.peers.add(("localhost", 3691))
    guardian.peers.add(("localhost", 3692))

    asyncio.run(guardian.start())