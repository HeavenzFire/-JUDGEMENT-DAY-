#!/usr/bin/env python3
"""
Embodied Swarm Simulation - Level 3 Integration
Wireless Resonance Consensus Movement for Object Manipulation

This simulation demonstrates 50 autonomous agents coordinating
to move a heavy object using only resonant field coupling,
without explicit communication or central control.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass, field
from typing import List, Tuple
import time

# Physics Constants
GRID_SIZE = 72
BASE_FREQ = 7.83  # Schumann resonance
COUPLING_K = 0.15
VACUUM_Z = 376.73

@dataclass
class SwarmAgent:
    """Individual agent in the embodied swarm"""
    id: int
    position: np.ndarray = field(default_factory=lambda: np.zeros(2))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2))
    phase: float = 0.0
    frequency: float = BASE_FREQ
    energy_state: float = 0.5
    quality_factor: float = 100.0
    attached_to_object: bool = False

@dataclass
class HeavyObject:
    """The object being manipulated by the swarm"""
    position: np.ndarray = field(default_factory=lambda: np.array([25.0, 25.0]))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2))
    mass: float = 1000.0  # Heavy object
    target_position: np.ndarray = field(default_factory=lambda: np.array([75.0, 75.0]))

class SyntropicGuardrail:
    """Prevents runaway resonance and destructive patterns"""

    def __init__(self):
        self.entropy_threshold = 0.8
        self.gain_limit = 10.0

    def scan_swarm(self, agents: List[SwarmAgent]) -> List[dict]:
        """Detect dangerous resonance patterns"""
        threats = []
        energies = [agent.energy_state for agent in agents]
        max_energy = max(energies)

        if max_energy > self.gain_limit:
            threats.append({
                'type': 'CRITICAL',
                'amplitude': max_energy,
                'description': 'Runaway resonance detected'
            })

        # Check for clustering (potential stampede)
        positions = np.array([agent.position for agent in agents])
        centroid = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - centroid, axis=1)
        if np.std(distances) < 2.0:  # Too clustered
            threats.append({
                'type': 'CLUSTER',
                'amplitude': np.std(distances),
                'description': 'Dangerous clustering detected'
            })

        return threats

    def apply_damping(self, agent: SwarmAgent, threats: List[dict]):
        """Apply negative feedback to dangerous patterns"""
        for threat in threats:
            if threat['type'] == 'CRITICAL':
                damping_factor = 0.3
                agent.energy_state -= threat['amplitude'] * damping_factor
                agent.quality_factor *= 0.95
            elif threat['type'] == 'CLUSTER':
                # Add random noise to break clustering
                agent.velocity += np.random.normal(0, 0.1, 2)

class EmbodiedSwarm:
    """Main swarm coordination system"""

    def __init__(self, num_agents: int = 50):
        self.agents = [SwarmAgent(i) for i in range(num_agents)]
        self.object = HeavyObject()
        self.guardrail = SyntropicGuardrail()

        # Initialize agent positions in a circle around object
        center = self.object.position
        radius = 10.0
        for i, agent in enumerate(self.agents):
            angle = 2 * np.pi * i / num_agents
            agent.position = center + radius * np.array([np.cos(angle), np.sin(angle)])

        # Simulation parameters
        self.dt = 0.1
        self.max_force = 5.0
        self.attach_distance = 3.0
        self.consensus_strength = 0.1

    def calculate_resonant_coupling(self, agent1: SwarmAgent, agent2: SwarmAgent) -> float:
        """Calculate wireless coupling strength between agents"""
        distance = np.linalg.norm(agent1.position - agent2.position)

        # Impedance-based coupling (lower impedance = stronger coupling)
        freq_diff = abs(agent1.frequency - agent2.frequency)
        phase_diff = abs(agent1.phase - agent2.phase)

        z_resonance = 1 + freq_diff * 50
        z_phase = 1 + np.sin(phase_diff / 2)
        impedance = VACUUM_Z * (1 / COUPLING_K) * z_resonance * z_phase

        # Distance attenuation
        coupling = 1000 / (impedance * (1 + distance))

        return max(0, coupling)

    def update_agent_physics(self, agent: SwarmAgent, neighbors: List[SwarmAgent]):
        """Update agent based on resonant interactions"""
        # Phase synchronization (Kuramoto model)
        phase_influence = 0
        freq_influence = 0
        position_influence = np.zeros(2)

        for neighbor in neighbors:
            coupling = self.calculate_resonant_coupling(agent, neighbor)
            if coupling > 0.1:  # Significant coupling threshold
                # Phase alignment
                phase_influence += coupling * np.sin(neighbor.phase - agent.phase)

                # Frequency entrainment
                freq_influence += coupling * (neighbor.frequency - agent.frequency)

                # Position consensus (for object manipulation)
                if neighbor.attached_to_object:
                    direction_to_object = self.object.position - agent.position
                    distance_to_object = np.linalg.norm(direction_to_object)
                    if distance_to_object < self.attach_distance:
                        agent.attached_to_object = True
                    else:
                        # Move toward object if neighbor is attached
                        position_influence += coupling * direction_to_object / distance_to_object

        # Apply influences
        agent.phase += agent.frequency * self.dt + self.consensus_strength * phase_influence * self.dt
        agent.phase %= 2 * np.pi

        agent.frequency += 0.01 * freq_influence * self.dt
        agent.frequency = np.clip(agent.frequency, BASE_FREQ * 0.8, BASE_FREQ * 1.2)

        # Movement
        if agent.attached_to_object:
            # Attached agents help move the object
            force_direction = self.object.target_position - self.object.position
            if np.linalg.norm(force_direction) > 1.0:
                force_direction = force_direction / np.linalg.norm(force_direction)
                agent.velocity = force_direction * self.max_force * agent.energy_state
            else:
                agent.velocity *= 0.9  # Slow down when close to target
        else:
            # Unattached agents move toward consensus position
            agent.velocity += position_influence * self.consensus_strength
            agent.velocity = np.clip(agent.velocity, -self.max_force, self.max_force)

        # Update position
        agent.position += agent.velocity * self.dt

        # Boundary conditions (toroidal)
        agent.position %= 100  # Assuming 100x100 arena

        # Update energy state
        agent.energy_state = 0.5 + 0.3 * np.cos(agent.phase) + 0.2 * np.random.normal()

    def update_object_physics(self):
        """Update the heavy object based on attached agents"""
        attached_agents = [agent for agent in self.agents if agent.attached_to_object]

        if attached_agents:
            # Calculate net force from attached agents
            net_force = np.zeros(2)
            for agent in attached_agents:
                force_magnitude = agent.energy_state * self.max_force
                force_direction = agent.velocity / (np.linalg.norm(agent.velocity) + 1e-6)
                net_force += force_magnitude * force_direction

            # Apply force to object (F = ma, so a = F/m)
            acceleration = net_force / self.object.mass
            self.object.velocity += acceleration * self.dt
            self.object.velocity *= 0.98  # Damping

            self.object.position += self.object.velocity * self.dt

            # Move attached agents with object
            for agent in attached_agents:
                agent.position = self.object.position + np.random.normal(0, 0.5, 2)

    def step_simulation(self):
        """Single simulation step"""
        # Apply syntropic guardrails
        threats = self.guardrail.scan_swarm(self.agents)
        if threats:
            print(f"[GUARDRAIL] 🛡️ Detected {len(threats)} threats, applying damping")
            for agent in self.agents:
                self.guardrail.apply_damping(agent, threats)

        # Update each agent
        for agent in self.agents:
            # Find neighbors within coupling range
            neighbors = []
            for other in self.agents:
                if other.id != agent.id and np.linalg.norm(other.position - agent.position) < 15.0:
                    neighbors.append(other)

            self.update_agent_physics(agent, neighbors)

        # Update object
        self.update_object_physics()

    def get_coherence_metric(self) -> float:
        """Calculate global swarm coherence"""
        phases = [agent.phase for agent in self.agents]
        mean_phase = np.mean(phases)
        coherence = np.abs(np.mean(np.exp(1j * np.array(phases))))
        return coherence

    def run_simulation(self, steps: int = 1000, visualize: bool = True):
        """Run the full simulation"""
        print(f"[SWARM] Starting Embodied Swarm Simulation with {len(self.agents)} agents")
        print(f"[OBJECTIVE] Move object from {self.object.position} to {self.object.target_position}")

        if visualize:
            self.setup_visualization()

        coherence_history = []

        for step in range(steps):
            self.step_simulation()
            coherence = self.get_coherence_metric()
            coherence_history.append(coherence)

            if step % 100 == 0:
                attached_count = sum(1 for agent in self.agents if agent.attached_to_object)
                distance_to_target = np.linalg.norm(self.object.position - self.object.target_position)
                print(".4f"
                      f"Attached: {attached_count}/{len(self.agents)}")

            if visualize and step % 10 == 0:
                self.update_visualization(step)

            # Check completion
            if np.linalg.norm(self.object.position - self.object.target_position) < 2.0:
                print(f"[SUCCESS] Object reached target at step {step}")
                break

        final_coherence = coherence_history[-1] if coherence_history else 0
        print(".4f")

        if visualize:
            plt.show()

        return {
            'steps': step,
            'final_coherence': final_coherence,
            'coherence_history': coherence_history,
            'final_position': self.object.position.copy()
        }

    def setup_visualization(self):
        """Setup matplotlib visualization"""
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Swarm plot
        self.ax1.set_xlim(0, 100)
        self.ax1.set_ylim(0, 100)
        self.ax1.set_title("Embodied Swarm - Object Manipulation")

        # Agent positions
        agent_positions = np.array([agent.position for agent in self.agents])
        self.agent_scatter = self.ax1.scatter(agent_positions[:, 0], agent_positions[:, 1],
                                            c='blue', alpha=0.6, label='Agents')

        # Object
        self.object_scatter = self.ax1.scatter(self.object.position[0], self.object.position[1],
                                             c='red', s=200, marker='s', label='Heavy Object')

        # Target
        self.target_scatter = self.ax1.scatter(self.object.target_position[0], self.object.target_position[1],
                                             c='green', s=100, marker='*', label='Target')

        self.ax1.legend()
        self.ax1.grid(True)

        # Coherence plot
        self.ax2.set_xlim(0, 1000)
        self.ax2.set_ylim(0, 1)
        self.ax2.set_title("Swarm Coherence Over Time")
        self.ax2.set_xlabel("Time Steps")
        self.ax2.set_ylabel("Coherence")
        self.coherence_line, = self.ax2.plot([], [], 'b-', label='Coherence')
        self.ax2.legend()
        self.ax2.grid(True)

        self.coherence_data = []

    def update_visualization(self, step):
        """Update visualization for current step"""
        # Update agent positions
        agent_positions = np.array([agent.position for agent in self.agents])
        colors = ['red' if agent.attached_to_object else 'blue' for agent in self.agents]
        self.agent_scatter.set_offsets(agent_positions)
        self.agent_scatter.set_color(colors)

        # Update object position
        self.object_scatter.set_offsets(self.object.position)

        # Update coherence plot
        coherence = self.get_coherence_metric()
        self.coherence_data.append(coherence)
        self.coherence_line.set_data(range(len(self.coherence_data)), self.coherence_data)

        self.ax2.set_xlim(0, max(100, len(self.coherence_data)))

        plt.pause(0.01)

if __name__ == "__main__":
    # Run the embodied swarm simulation
    swarm = EmbodiedSwarm(num_agents=50)
    results = swarm.run_simulation(steps=1000, visualize=True)

    print("\n[RESULTS]")
    print(f"Simulation completed in {results['steps']} steps")
    print(".4f")
    print(f"Final object position: {results['final_position']}")
    print(f"Target position: {swarm.object.target_position}")