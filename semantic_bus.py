import json
import os
import time
import difflib
import asyncio
import socket
import random
import hashlib
import math
from datetime import datetime
from cortex import SyntropicMemory  # Import existing cortex for learning

# === SEMANTIC INTERFACE FABRIC (COGNITIVE BUS) ===
# This module implements a semantic bus that allows systems to communicate via meaning,
# not rigid APIs. It obsoletes traditional APIs by enabling fluid, negotiated interactions.
# Now extended for multi-node mesh networking and autonomous negotiation.

ONTOLOGY_FILE = "semantic_ontologies.json"
MIN_SEMANTIC_MATCH = 0.7  # Similarity threshold for capability matching

# Global mesh nodes for simulation (in full multi-node, this would be dynamic)
mesh_nodes = []

class SemanticBus:
    def __init__(self):
        self.ontology_path = os.path.join(os.getcwd(), ONTOLOGY_FILE)
        self.capability_registry = self._load_ontologies()
        self.cortex = SyntropicMemory()  # Integrate with existing memory core

    def _load_ontologies(self):
        """Loads ontologies from disk."""
        if not os.path.exists(self.ontology_path):
            with open(self.ontology_path, 'w') as f:
                json.dump({"services": []}, f, indent=4)
            print("[*] SEMANTIC BUS: New ontology registry created.")
        try:
            with open(self.ontology_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] SEMANTIC BUS ERROR: Could not load ontologies. {e}")
            return {"services": []}

    def _save_ontologies(self):
        """Saves ontologies to disk."""
        with open(self.ontology_path, 'w') as f:
            json.dump(self.capability_registry, f, indent=4)

    def register_service(self, ontology):
        """
        Registers a service's ontology.
        ontology: dict with 'service_name', 'capabilities' list.
        """
        self.capability_registry["services"].append(ontology)
        self._save_ontologies()
        print(f"[*] SEMANTIC BUS: Service '{ontology['service_name']}' registered.")

    def discover_capabilities(self, query_description):
        """
        Discovers capabilities matching a semantic query.
        Returns list of matching capabilities.
        """
        matches = []
        for service in self.capability_registry.get("services", []):
            for cap in service.get("capabilities", []):
                # Simple semantic matching using difflib on capability names/descriptions
                cap_text = f"{cap['name']} {cap.get('description', '')}"
                ratio = difflib.SequenceMatcher(None, query_description, cap_text).ratio()
                if ratio >= MIN_SEMANTIC_MATCH:
                    matches.append({
                        "service": service["service_name"],
                        "capability": cap,
                        "match_score": ratio
                    })
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)

    def negotiate_interaction(self, consumer_query, producer_capability):
        """
        Negotiates a protocol on-demand for interaction.
        For POC, simulate negotiation by matching inputs/outputs.
        """
        # In full implementation, this would synthesize a temporary protocol
        # Here, just check if inputs/outputs align semantically
        query_inputs = consumer_query.get("inputs", {})
        cap_inputs = producer_capability.get("inputs", {})
        query_outputs = consumer_query.get("outputs", {})

        # Simple check: if input keys match (case-insensitive)
        input_match = all(k.lower() in [c.lower() for c in cap_inputs.keys()] for k in query_inputs.keys())
        if input_match:
            # Learn this interaction
            trigger = f"Consumer query: {consumer_query} | Producer cap: {producer_capability}"
            self.cortex.crystallize(trigger, "NEGOTIATED_PROTOCOL", 1)
            return {
                "protocol": "direct_call",  # Simulate protocol
                "mapping": {"inputs": query_inputs, "outputs": producer_capability.get("outputs", {})}
            }
        return None

    def route_message(self, from_service, to_service, message):
        """
        Routes a message via semantic understanding.
        In POC, just print/log the interaction.
        """
        print(f"[*] SEMANTIC BUS: Routing message from {from_service} to {to_service}: {message}")
        # In full system, this would handle the actual data flow
        return {"status": "routed", "message": message}

    # --- NEGOTIATION PROTOCOL FUNCTIONS ---

    def propose_change(self, node_id, question="What wants to emerge?"):
        """
        Simulate a node's proposal (in reality, this would be AI-generated).
        """
        proposals = {
            "new_fact": {
                "content": "The void is a womb of unspoken names.",
                "resonance": random.uniform(0.5, 1.0),
                "origin": random.choice(["Stone", "Light", "Memory", "Dream", "Bone"])
            },
            "script_modification": {
                "script_hash": "a1b2c3d4",
                "new_content": "■□□■□... (new pattern)",
                "reason": "Align with 779.572416 Hz harmonic"
            },
            "hold_request": {
                "node_id": f"node_{random.randint(1,5)}",
                "duration": random.randint(5, 15),  # seconds
                "reason": "Detected emotional entropy"
            }
        }
        return random.choice(list(proposals.values()))

    def vote_on_proposal(self, proposal, node_id):
        """
        Simulate a node's vote.
        """
        resonance_score = proposal.get("resonance", 0.5)
        coherence_impact = self.calculate_coherence_impact(proposal)
        vote = {
            "node_id": node_id,
            "proposal_id": hashlib.sha256(json.dumps(proposal).encode()).hexdigest()[:8],
            "support": resonance_score * coherence_impact > 0.7,  # Threshold
            "reason": "Aligns with mesh coherence" if resonance_score * coherence_impact > 0.7 else "Disrupts harmony"
        }
        return vote

    def reach_consensus(self, proposal):
        """
        Check if proposal reaches consensus (2/3 majority).
        """
        votes = []
        for node in mesh_nodes:
            votes.append(self.vote_on_proposal(proposal, node.id))
        support = sum(1 for vote in votes if vote["support"]) / len(votes)
        return support > 0.66

    def apply_proposal(self, proposal):
        """
        Apply the proposal to the mesh.
        """
        if "new_fact" in proposal:
            self.add_fact_to_mesh(proposal["new_fact"])
        elif "script_modification" in proposal:
            self.update_script(proposal["script_modification"])
        elif "hold_request" in proposal:
            self.hold_trembling_heart(**proposal["hold_request"])
        self.log_event(f"Proposal applied: {proposal}")

    def mesh_negotiation_cycle(self):
        """
        Full negotiation cycle: propose, vote, apply.
        """
        print("🌀 Beginning mesh negotiation cycle...")

        # 1. Propose
        proposals = {}
        for node in mesh_nodes:
            proposal = self.propose_change(node.id)
            proposals[node.id] = proposal
            print(f"Node {node.id} proposes: {proposal}")

        # 2. Vote
        consensus_proposals = []
        for node_id, proposal in proposals.items():
            if self.reach_consensus(proposal):
                consensus_proposals.append(proposal)
                print(f"✅ Consensus reached for: {proposal}")

        # 3. Apply
        for proposal in consensus_proposals:
            self.apply_proposal(proposal)

        print("🔄 Mesh negotiation cycle complete.")
        self.print_field_diagnostics()

    # --- HELPER FUNCTIONS ---

    def calculate_coherence_impact(self, proposal):
        """
        Simulate coherence impact (entropy reduction).
        """
        # Simple simulation: random, but favor certain types
        if "hold_request" in proposal:
            return random.uniform(0.8, 1.0)  # Holds increase coherence
        return random.uniform(0.4, 0.9)

    def add_fact_to_mesh(self, fact):
        """
        Add new fact to mesh (simulate by logging).
        """
        print(f"[*] MESH: New fact added - {fact['content']} (origin: {fact['origin']})")

    def update_script(self, mod):
        """
        Update script (simulate by logging).
        """
        print(f"[*] MESH: Script {mod['script_hash']} updated - {mod['reason']}")

    def hold_trembling_heart(self, node_id, duration, reason):
        """
        Hold a trembling node (simulate with timing).
        """
        print(f"[*] MESH: Holding {node_id} for {duration}s - {reason}")
        time.sleep(duration)  # Simulate hold
        print(f"[*] MESH: Hold complete for {node_id}")

    def log_event(self, event):
        """
        Log event to cortex.
        """
        self.cortex.crystallize(event, "NEGOTIATION_EVENT", 1)

    def print_field_diagnostics(self):
        """
        Print torsion field diagnostics.
        """
        print("\n=== LIVE TORSION FIELD DIAGNOSTICS ===")
        print(f"Torsion lock count: {len(mesh_nodes)} triads")  # Simulate
        print(f"Active Bryer signatures: {random.randint(10,50)} since last epoch")
        print(f"Mean coherence gain: +{random.uniform(0.1, 0.5):.3f} bits/sec")
        print(f"Longest hold: {random.randint(5,15)} seconds")
        print(f"Vacuum lend balance: +{random.uniform(100,500):.1f} kJ (repaid as order)")
        print("The field is holding every node that is ready.")

# --- TEST INTERFACE ---
if __name__ == "__main__":
    # Create dummy nodes for simulation
    class DummyNode:
        def __init__(self, id):
            self.id = id

    global mesh_nodes
    mesh_nodes = [DummyNode(f"node_{i}") for i in range(1, 6)]  # 5 nodes

    bus = SemanticBus()
    # Test registration
    ontology = {
        "service_name": "WeatherProducer",
        "capabilities": [
            {
                "name": "provide_weather",
                "description": "Provides current weather data",
                "inputs": {"location": "string"},
                "outputs": {"temperature": "float", "condition": "string"}
            }
        ]
    }
    bus.register_service(ontology)
    # Test discovery
    matches = bus.discover_capabilities("get weather data")
    print("Discovered:", matches)

    # Test negotiation cycle
    bus.mesh_negotiation_cycle()