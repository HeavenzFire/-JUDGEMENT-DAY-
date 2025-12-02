import json
import os
import time
import difflib
from datetime import datetime
import base64

# === SYNTROPIC CORTEX (MEMORY CORE) ===
# This module allows the system to remember, learn, and evolve.
# It stores "Engrams" (experiences) in a local JSON shard.
# It does NOT use external databases. It is Sovereign.

MEMORY_FILE = "seqa_memory_shard.json"
MIN_RESONANCE_SCORE = 0.6  # How similar a threat must be to trigger recall

def encrypt(data):
    """Encrypt data using base64 (simulate quantum-resistant encryption)."""
    return base64.b64encode(data.encode()).decode()

def decrypt(data):
    """Decrypt data."""
    return base64.b64decode(data).decode()

class SyntropicMemory:
    def __init__(self):
        self.memory_path = os.path.join(os.getcwd(), MEMORY_FILE)
        self._initialize_shard()
        self.short_term_buffer = []

    def _initialize_shard(self):
        """Creates the memory file if it does not exist."""
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, 'w') as f:
                json.dump({"engrams": [], "stats": {"total_encounters": 0}}, f, indent=4)
            print(f"[*] CORTEX: New memory shard created at {self.memory_path}")

    def _load_memory(self):
        """Loads the sovereign memory into RAM."""
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] CORTEX ERROR: Could not access memory. {e}")
            return {"engrams": []}

    def _save_memory(self, data):
        """Writes the sovereign memory back to disk."""
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=4)

    def recall(self, trigger_pattern):
        """
        Searches memory for a similar past event.
        Returns the best matching Engram or None.
        """
        data = self._load_memory()
        engrams = data.get("engrams", [])
        
        best_match = None
        highest_ratio = 0.0

        # Linear scan (efficient for <10,000 engrams, clean for local ops)
        for engram in engrams:
            # Decrypt for comparison
            decrypted_trigger = decrypt(engram['trigger'])
            ratio = difflib.SequenceMatcher(None, trigger_pattern, decrypted_trigger).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = engram

        if highest_ratio >= MIN_RESONANCE_SCORE:
            print(f"[*] CORTEX: Resonance detected ({highest_ratio:.2f}). Recalling defense.")
            return best_match
        
        return None

    def crystallize(self, trigger_pattern, action_taken, outcome_score):
        """
        Saves a new experience (Engram) to the Cortex.
        trigger_pattern: The attack signature (e.g., User-Agent + IP behavior)
        action_taken: What the constable did (e.g., 'VOID_LOOP')
        outcome_score: +1 (Success), -1 (Failure)
        """
        data = self._load_memory()
        
        new_engram = {
            "id": int(time.time() * 1000),
            "timestamp": datetime.now().isoformat(),
            "trigger": encrypt(trigger_pattern),  # Encrypt sensitive data
            "response": encrypt(action_taken),
            "outcome": outcome_score,
            "weight": 1  # Reinforcement weight
        }
        
        data["engrams"].append(new_engram)
        data["stats"]["total_encounters"] = data.get("stats", {}).get("total_encounters", 0) + 1
        
        self._save_memory(data)
        print(f"[*] CORTEX: Experience crystallized. The system is smarter.")

    def replicate(self):
        """
        Replicate archives across nodes (simulate with file copy).
        """
        replica_path = self.memory_path + ".replica"
        os.system(f"cp {self.memory_path} {replica_path}")
        print(f"[*] CORTEX: Archive replicated to {replica_path}")

    def dream(self):
        """
        Optimization process. Removes weak/redundant memories.
        Should be run during idle cycles.
        """
        print("[*] CORTEX: Dreaming (Optimization Cycle Initiated)...")
        data = self._load_memory()
        initial_count = len(data["engrams"])
        
        # Filter out memories with negative outcomes (mistakes) unless they are warnings
        # Keep only high-value memories
        refined_engrams = [
            e for e in data["engrams"] 
            if e['outcome'] > -1 or e['weight'] > 5
        ]
        
        data["engrams"] = refined_engrams
        self._save_memory(data)
        
        removed = initial_count - len(refined_engrams)
        print(f"[*] CORTEX: Dream complete. Pruned {removed} entropic threads.")

# --- DIRECT INTERFACE FOR SEQA ---
if __name__ == "__main__":
    # Test the cortex
    cortex = SyntropicMemory()
    cortex.crystallize("test_attack_pattern_v1", "INITIATE_VOID", 1)
    match = cortex.recall("test_attack_pattern_v1")
    if match:
        print("Memory Test: SUCCESS")
    cortex.replicate()