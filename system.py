import time
import json
import os
from typing import Dict, List, Optional
from nodes import (
    Node, SelfKnowledgeNode, InnerLightNode, UnityNode, SelfImageKernel,
    VisualizationModule, ServoMindMechanism, CalmConfidenceFilter,
    ErrorFeedbackMonitor, ManifestationEngine, PurposeEngine,
    AdaptiveConnectivityGraph, MemoryMesh, PlasticitySimulator
)

class MetaSystem:
    def __init__(self, config_path: Optional[str] = None):
        self.nodes: Dict[str, Node] = {}
        self.loops: List[str] = [
            "Self-Actualization",
            "Mental Calibration",
            "Error Feedback",
            "Manifestation"
        ]
        self.syntropy_score = 0.5  # Measure of order and coherence
        self.resilience = 0.5
        self.generativity = 0.5
        self.autonomy = 0.5
        self.last_cycle_time = time.time()
        self.config_path = config_path or "/vercel/sandbox/config.yaml"
        self.state_path = "/vercel/sandbox/system_state.json"
        self.initialize_nodes()
        self.load_state()

    def initialize_nodes(self):
        # Spiritual/Archetypal Layer
        self.nodes["Self-Knowledge Node"] = SelfKnowledgeNode()
        self.nodes["Inner Light Node"] = InnerLightNode()
        self.nodes["Unity Node"] = UnityNode()

        # Psycho-Cybernetics Control Layer
        self.nodes["Self-Image Kernel"] = SelfImageKernel()
        self.nodes["Visualization Module"] = VisualizationModule()
        self.nodes["Servo-Mind Mechanism"] = ServoMindMechanism()
        self.nodes["Calm/Confidence Filter"] = CalmConfidenceFilter()
        self.nodes["Error/Feedback Monitor"] = ErrorFeedbackMonitor()

        # Behavioral/Output Layer
        self.nodes["Manifestation Engine"] = ManifestationEngine()
        self.nodes["Purpose Engine"] = PurposeEngine()

        # Neuromorphic Dynamics Layer
        self.nodes["Adaptive Connectivity Graph"] = AdaptiveConnectivityGraph()
        self.nodes["Memory Mesh"] = MemoryMesh()
        self.nodes["Plasticity Simulator"] = PlasticitySimulator()

    def run_cycle(self, external_inputs: Dict[str, float] = None):
        if external_inputs is None:
            external_inputs = {}

        current_time = time.time()
        delta_time = current_time - self.last_cycle_time
        self.last_cycle_time = current_time

        # Collect inputs for each node
        node_inputs = self.collect_inputs(external_inputs)

        # Update all nodes
        for node_name, node in self.nodes.items():
            inputs = node_inputs.get(node_name, {})
            node.update(inputs, delta_time)

        # Run feedback loops
        self.run_feedback_loops(delta_time)

        # Update system metrics
        self.update_system_metrics()

        # Save state periodically
        if int(current_time) % 60 == 0:  # Every minute
            self.save_state()

    def collect_inputs(self, external_inputs: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        inputs = {}
        for node_name, node in self.nodes.items():
            node_inputs = {}
            # Add external inputs
            for ext_key, ext_val in external_inputs.items():
                if ext_key in node_name.lower() or ext_key == "global":
                    node_inputs[ext_key] = ext_val

            # Add internal connections (simplified)
            if node_name == "Self-Knowledge Node":
                node_inputs["Inner Light Node"] = self.nodes["Inner Light Node"].get_output()
                node_inputs["Unity Node"] = self.nodes["Unity Node"].get_output()
            elif node_name == "Inner Light Node":
                node_inputs["Self-Knowledge Node"] = self.nodes["Self-Knowledge Node"].get_output()
            elif node_name == "Unity Node":
                node_inputs["Inner Light Node"] = self.nodes["Inner Light Node"].get_output()
            elif node_name == "Self-Image Kernel":
                node_inputs["archetype_alignment"] = (self.nodes["Inner Light Node"].get_output() + self.nodes["Unity Node"].get_output()) / 2
                node_inputs["feedback"] = self.nodes["Error/Feedback Monitor"].get_output()
            elif node_name == "Visualization Module":
                node_inputs["Purpose Engine"] = self.nodes["Purpose Engine"].get_output()
            elif node_name == "Servo-Mind Mechanism":
                node_inputs["Self-Image Kernel"] = self.nodes["Self-Image Kernel"].get_output()
                node_inputs["Visualization Module"] = self.nodes["Visualization Module"].get_output()
                node_inputs["Calm/Confidence Filter"] = self.nodes["Calm/Confidence Filter"].get_output()
            elif node_name == "Error/Feedback Monitor":
                node_inputs["outcome"] = self.nodes["Manifestation Engine"].get_output()
                node_inputs["goal_vector"] = self.nodes["Visualization Module"].get_output()
            elif node_name == "Manifestation Engine":
                node_inputs["Servo-Mind Mechanism"] = self.nodes["Servo-Mind Mechanism"].get_output()
                node_inputs["ethics"] = 0.9  # Placeholder for ethics score
            elif node_name == "Adaptive Connectivity Graph":
                node_inputs["coherence"] = self.syntropy_score
            elif node_name == "Memory Mesh":
                node_inputs["syntropy"] = self.syntropy_score
            elif node_name == "Plasticity Simulator":
                node_inputs["rules"] = 0.8  # Graceful update rules

            inputs[node_name] = node_inputs

        return inputs

    def run_feedback_loops(self, delta_time: float):
        # Self-Actualization Loop: Inner Light -> Self-Knowledge -> Self-Image
        inner_light = self.nodes["Inner Light Node"].get_output()
        self_knowledge = self.nodes["Self-Knowledge Node"].get_output()
        self_image = self.nodes["Self-Image Kernel"]
        self_image.state = max(0.0, min(1.0, self_image.state + (inner_light + self_knowledge) * 0.02 * delta_time))

        # Mental Calibration Loop: Error Feedback -> Self-Image -> Visualization
        error_feedback = self.nodes["Error/Feedback Monitor"].get_output()
        visualization = self.nodes["Visualization Module"]
        visualization.state = max(0.0, min(1.0, visualization.state + error_feedback * 0.03 * delta_time))

        # Manifestation Loop: Servo-Mind -> Manifestation -> Outcome (simulated)
        servo = self.nodes["Servo-Mind Mechanism"].get_output()
        manifestation = self.nodes["Manifestation Engine"]
        manifestation.state = max(0.0, min(1.0, manifestation.state + servo * 0.04 * delta_time))

    def update_system_metrics(self):
        # Calculate syntropy (coherence) as average node state variance (lower variance = higher syntropy)
        states = [node.get_output() for node in self.nodes.values()]
        mean_state = sum(states) / len(states)
        variance = sum((s - mean_state)**2 for s in states) / len(states)
        self.syntropy_score = max(0.0, 1.0 - variance)  # Higher coherence = higher syntropy

        # Resilience: Ability to maintain syntropy under perturbation
        self.resilience = min(1.0, self.syntropy_score + 0.1)

        # Generativity: Rate of positive change in node states
        total_change = sum(abs(node.get_output() - 0.5) for node in self.nodes.values()) / len(self.nodes)
        self.generativity = min(1.0, total_change)

        # Autonomy: Independence from external inputs (placeholder)
        self.autonomy = 0.7

    def get_status(self) -> Dict:
        return {
            "syntropy_score": self.syntropy_score,
            "resilience": self.resilience,
            "generativity": self.generativity,
            "autonomy": self.autonomy,
            "node_states": {name: node.get_output() for name, node in self.nodes.items()},
            "last_cycle_time": self.last_cycle_time
        }

    def save_state(self):
        state = {
            "nodes": {name: {"state": node.state, "last_update": node.last_update} for name, node in self.nodes.items()},
            "system_metrics": {
                "syntropy_score": self.syntropy_score,
                "resilience": self.resilience,
                "generativity": self.generativity,
                "autonomy": self.autonomy
            },
            "last_cycle_time": self.last_cycle_time
        }
        with open(self.state_path, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            for name, node_state in state.get("nodes", {}).items():
                if name in self.nodes:
                    self.nodes[name].state = node_state["state"]
                    self.nodes[name].last_update = node_state["last_update"]
            metrics = state.get("system_metrics", {})
            self.syntropy_score = metrics.get("syntropy_score", 0.5)
            self.resilience = metrics.get("resilience", 0.5)
            self.generativity = metrics.get("generativity", 0.5)
            self.autonomy = metrics.get("autonomy", 0.5)
            self.last_cycle_time = state.get("last_cycle_time", time.time())

if __name__ == "__main__":
    system = MetaSystem()
    print("Meta-System initialized.")
    for _ in range(10):
        system.run_cycle({"global": 0.1})  # Small external input
        status = system.get_status()
        print(f"Cycle: Syntropy {status['syntropy_score']:.2f}, Resilience {status['resilience']:.2f}")
        time.sleep(1)