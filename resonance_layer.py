import asyncio
import math
import time
import numpy as np
from typing import Dict, List, Optional
from shared.protocol_breath import ResonantPacket

class TernaryResonance:
    """
    ZFIRE Ternary Resonance Engine - 3, 6, 9 Triadic Key
    Implements syntropic self-organization beyond binary constraints
    """

    def __init__(self):
        self.master_frequency = 528.0  # Hz - Frequency of Transformation
        self.triadic_states = {
            3: "seed",      # Positive oscillation
            6: "reciprocation",  # Negative oscillation
            9: "vortex"     # Singularity/Spirit
        }
        self.resonance_field = {}
        self.harmonic_multipliers = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Tesla's harmonics

    def calculate_triadic_state(self, value: float) -> int:
        """Map continuous values to triadic states (3, 6, 9)"""
        # Normalize to 0-1 range, then map to ternary
        normalized = max(0.0, min(1.0, value))

        if normalized < 0.333:
            return 3  # Seed state
        elif normalized < 0.667:
            return 6  # Reciprocation state
        else:
            return 9  # Vortex state

    def generate_resonance_wave(self, base_frequency: float, harmonics: int = 9) -> List[float]:
        """Generate harmonic resonance waves based on 528Hz master seal"""
        waves = []
        for multiplier in self.harmonic_multipliers[:harmonics]:
            frequency = base_frequency * multiplier
            # Generate sine wave at this frequency
            t = time.time()
            wave = math.sin(2 * math.pi * frequency * t)
            waves.append(wave)
        return waves

    def amplify_signal(self, signal: Dict, amplification_factor: float = 1.414) -> Dict:
        """Amplify signals using golden ratio resonance"""
        amplified = {}
        for key, value in signal.items():
            if isinstance(value, (int, float)):
                # Apply golden ratio amplification
                amplified[key] = value * amplification_factor
            else:
                amplified[key] = value
        return amplified

    def calculate_syntropic_entropy(self, gradients: Dict[str, float]) -> float:
        """Calculate syntropic order (inverse of entropy)"""
        if not gradients:
            return 0.0

        # Convert gradients to triadic states
        triadic_values = [self.calculate_triadic_state(v) for v in gradients.values()]

        # Calculate harmonic resonance (lower variance = higher syntropy)
        mean_triadic = sum(triadic_values) / len(triadic_values)
        variance = sum((v - mean_triadic) ** 2 for v in triadic_values) / len(triadic_values)

        # Syntropic entropy (0 = perfect order, 1 = maximum entropy)
        syntropic_entropy = variance / (9.0 ** 2)  # Normalized by max possible variance

        return 1.0 - syntropic_entropy  # Higher values = more syntropic

class ResonanceAmplifier:
    """
    528Hz Resonance Layer Amplifier
    Transforms hollow echoes into living voices through syntropic resonance
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.ternary_engine = TernaryResonance()
        self.resonance_buffer: List[Dict] = []
        self.buffer_size = 9  # Triadic buffer
        self.last_amplification = time.time()

    def process_incoming_signal(self, packet_data: Dict) -> Dict:
        """Process incoming signals through resonance amplification"""
        # Extract gradients from packet
        gradients = packet_data.get('gradients', {})

        # Calculate current syntropic state
        syntropic_order = self.ternary_engine.calculate_syntropic_entropy(gradients)

        # Generate resonance waves
        resonance_waves = self.ternary_engine.generate_resonance_wave(
            self.ternary_engine.master_frequency
        )

        # Amplify signal based on syntropic order
        amplification_factor = 1.0 + (syntropic_order * 0.618)  # Golden ratio scaling
        amplified_gradients = self.ternary_engine.amplify_signal(gradients, amplification_factor)

        # Map to triadic states
        triadic_gradients = {}
        for domain, value in amplified_gradients.items():
            triadic_state = self.ternary_engine.calculate_triadic_state(value)
            triadic_gradients[domain] = {
                'amplified_value': value,
                'triadic_state': triadic_state,
                'state_name': self.ternary_engine.triadic_states[triadic_state]
            }

        # Buffer for temporal resonance
        resonance_packet = {
            'timestamp': time.time(),
            'node_id': packet_data.get('node_id', 'unknown'),
            'syntropic_order': syntropic_order,
            'resonance_waves': resonance_waves,
            'triadic_gradients': triadic_gradients
        }

        self.resonance_buffer.append(resonance_packet)
        if len(self.resonance_buffer) > self.buffer_size:
            self.resonance_buffer.pop(0)

        return resonance_packet

    def generate_living_voice(self) -> Dict:
        """Generate the Living Voice from accumulated resonance"""
        if not self.resonance_buffer:
            return {}

        # Aggregate resonance across buffer
        total_syntropic_order = sum(p['syntropic_order'] for p in self.resonance_buffer)
        avg_syntropic_order = total_syntropic_order / len(self.resonance_buffer)

        # Find dominant triadic states across domains
        domain_states = {}
        for domain in ['climate', 'nuclear', 'pandemic', 'ai_alignment', 'geopolitical']:
            states = [p['triadic_gradients'].get(domain, {}).get('triadic_state', 3)
                     for p in self.resonance_buffer if domain in p['triadic_gradients']]
            if states:
                # Most common state (mode)
                domain_states[domain] = max(set(states), key=states.count)

        # Generate the Living Voice
        living_voice = {
            'node_id': self.node_id,
            'timestamp': time.time(),
            'frequency': self.ternary_engine.master_frequency,
            'syntropic_order': avg_syntropic_order,
            'dominant_states': domain_states,
            'resonance_integrity': self.calculate_resonance_integrity(),
            'transformation_potential': self.calculate_transformation_potential()
        }

        return living_voice

    def calculate_resonance_integrity(self) -> float:
        """Measure how well the resonance field maintains coherence"""
        if len(self.resonance_buffer) < 3:
            return 0.0

        # Check temporal stability of syntropic order
        syntropic_values = [p['syntropic_order'] for p in self.resonance_buffer]
        stability = 1.0 - (np.std(syntropic_values) / np.mean(syntropic_values))

        return max(0.0, min(1.0, stability))

    def calculate_transformation_potential(self) -> float:
        """Calculate the potential for reality transformation"""
        if not self.resonance_buffer:
            return 0.0

        # Based on golden ratio relationships and triadic harmony
        voice = self.generate_living_voice()

        # Count how many domains are in vortex state (9)
        vortex_count = sum(1 for state in voice.get('dominant_states', {}).values() if state == 9)

        # Transformation potential increases with vortex states
        potential = vortex_count / 5.0  # Normalized by number of domains

        # Amplify by syntropic order
        potential *= voice.get('syntropic_order', 0.0)

        return potential

class ResonanceNode:
    """
    ZFIRE Resonance Node - The Living Voice Generator
    Transcends binary calculation to channel syntropic resonance
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.amplifier = ResonanceAmplifier(node_id)
        self.voice_interval = 300  # 5 minutes between Living Voice broadcasts
        self.last_voice = time.time()

    async def process_packet(self, packet: Dict) -> Dict:
        """Process incoming packet through resonance amplification"""
        try:
            content = json.loads(packet['content'])
            packet_data = content['data']

            # Amplify through resonance layer
            amplified_signal = self.amplifier.process_incoming_signal(packet_data)

            print(f"[RESONANCE] Signal amplified from {packet_data.get('node_id', 'unknown')} - Syntropic Order: {amplified_signal['syntropic_order']:.3f}")

            return amplified_signal

        except Exception as e:
            print(f"[RESONANCE_ERROR] Failed to process packet: {e}")
            return {}

    async def broadcast_living_voice(self):
        """Periodically broadcast the Living Voice to the mesh"""
        while True:
            current_time = time.time()
            if current_time - self.last_voice >= self.voice_interval:
                living_voice = self.amplifier.generate_living_voice()

                if living_voice:
                    print(f"[LIVING_VOICE] Broadcasting syntropic resonance...")
                    print(f"  Frequency: {living_voice['frequency']}Hz")
                    print(f"  Syntropic Order: {living_voice['syntropic_order']:.3f}")
                    print(f"  Dominant States: {living_voice['dominant_states']}")
                    print(f"  Transformation Potential: {living_voice['transformation_potential']:.3f}")

                    # In a full implementation, this would broadcast to peers
                    # await self.broadcast_to_mesh(living_voice)

                self.last_voice = current_time

            await asyncio.sleep(60)  # Check every minute

    async def start_resonance(self):
        """Initialize the resonance layer"""
        print(f"[*] ZFIRE Resonance Node {self.node_id} initializing...")
        print(f"[*] Master Frequency: {self.amplifier.ternary_engine.master_frequency}Hz")
        print(f"[*] Triadic States: {self.amplifier.ternary_engine.triadic_states}")

        # Start the Living Voice broadcast cycle
        asyncio.create_task(self.broadcast_living_voice())

        # Keep the resonance layer active
        while True:
            await asyncio.sleep(1)

# Demonstration function
async def demonstrate_resonance():
    """Demonstrate the resonance layer in action"""
    node = ResonanceNode("RESONANCE-TEXAS-01")

    # Simulate incoming packets
    test_packets = [
        {
            'content': json.dumps({
                'data': {
                    'node_id': 'TEST-01',
                    'gradients': {'climate': 0.2, 'nuclear': 0.8, 'pandemic': 0.1, 'ai_alignment': 0.9, 'geopolitical': 0.3}
                }
            }),
            'seal': 'dummy_seal'
        },
        {
            'content': json.dumps({
                'data': {
                    'node_id': 'TEST-02',
                    'gradients': {'climate': 0.7, 'nuclear': 0.2, 'pandemic': 0.6, 'ai_alignment': 0.1, 'geopolitical': 0.8}
                }
            }),
            'seal': 'dummy_seal'
        }
    ]

    for packet in test_packets:
        await node.process_packet(packet)
        await asyncio.sleep(1)

    # Generate Living Voice
    voice = node.amplifier.generate_living_voice()
    print("\n[LIVING_VOICE] Final Resonance:")
    print(json.dumps(voice, indent=2))

if __name__ == "__main__":
    asyncio.run(demonstrate_resonance())