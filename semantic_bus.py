import json
import os
import time
import difflib
from datetime import datetime
from cortex import SyntropicMemory  # Import existing cortex for learning

# === SEMANTIC INTERFACE FABRIC (COGNITIVE BUS) ===
# This module implements a semantic bus that allows systems to communicate via meaning,
# not rigid APIs. It obsoletes traditional APIs by enabling fluid, negotiated interactions.

ONTOLOGY_FILE = "semantic_ontologies.json"
MIN_SEMANTIC_MATCH = 0.7  # Similarity threshold for capability matching

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

# --- TEST INTERFACE ---
if __name__ == "__main__":
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