import asyncio
import hashlib
import json
from datetime import datetime
import random

# === SEMANTIC BUS WITH LIFE-PRIORITIZED AND ETHICAL FACTS ===
class SemanticBus:
    def __init__(self, node_id):
        self.node_id = node_id
        self.facts = {}  # key: fact_id, value: {fact, proof, scope, timestamp, priority}
        self.subscribers = []
        self.peers = []

    def add_fact(self, fact, proof, scope, priority):
        """Adds a fact with ethical checks and prioritization."""
        if not proof or not isinstance(proof, str):
            raise ValueError("Proof must be a non-empty string for ethical validation.")
        fact_id = hashlib.sha256(json.dumps(fact, sort_keys=True).encode()).hexdigest()
        timestamp = datetime.now()
        self.facts[fact_id] = {
            'fact': fact,
            'proof': proof,
            'scope': scope,
            'timestamp': timestamp,
            'priority': priority
        }
        print(f"[*] SEMANTIC BUS: Fact added with ID {fact_id}, priority {priority}.")
        return fact_id

    def get_fact(self, fact_id):
        """Retrieves a fact by ID."""
        return self.facts.get(fact_id)

    def get_prioritized_facts(self):
        """Returns facts sorted by priority (highest first)."""
        return sorted(self.facts.items(), key=lambda x: x[1]['priority'], reverse=True)

    def subscribe(self, subscriber):
        """Adds a subscriber (async callable)."""
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            print(f"[*] SEMANTIC BUS: Subscriber added.")

    def unsubscribe(self, subscriber):
        """Removes a subscriber."""
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            print(f"[*] SEMANTIC BUS: Subscriber removed.")

    def add_peer(self, peer):
        """Adds a peer node."""
        if peer not in self.peers:
            self.peers.append(peer)
            print(f"[*] SEMANTIC BUS: Peer added.")

    def remove_peer(self, peer):
        """Removes a peer node."""
        if peer in self.peers:
            self.peers.remove(peer)
            print(f"[*] SEMANTIC BUS: Peer removed.")

    async def publish_fact(self, fact_id):
        """Publishes a fact to subscribers and peers asynchronously."""
        fact = self.facts.get(fact_id)
        if not fact:
            print(f"[!] SEMANTIC BUS: Fact {fact_id} not found.")
            return
        tasks = []
        for subscriber in self.subscribers:
            tasks.append(asyncio.create_task(subscriber(fact)))
        for peer in self.peers:
            if hasattr(peer, 'receive_fact'):
                tasks.append(asyncio.create_task(peer.receive_fact(fact)))
        await asyncio.gather(*tasks)
        print(f"[*] SEMANTIC BUS: Fact {fact_id} published.")

    async def receive_fact(self, fact):
        """Receives a fact from a peer (for propagation)."""
        # For simplicity, just print; in full system, integrate with local facts
        print(f"[*] SEMANTIC BUS: Received fact: {fact['fact']}")

# --- TEST INTERFACE ---
if __name__ == "__main__":
    async def test():
        bus = SemanticBus("node_1")
        # Test adding facts
        fact_id1 = bus.add_fact({"event": "life_prioritized"}, "verified_proof", "global", 5)
        fact_id2 = bus.add_fact({"event": "ethical_check"}, "proof_data", "local", 3)
        # Test prioritization
        prioritized = bus.get_prioritized_facts()
        print("Prioritized facts:", [fid for fid, _ in prioritized])
        # Test subscribers
        async def mock_subscriber(fact):
            print(f"Subscriber notified: {fact['fact']}")
        bus.subscribe(mock_subscriber)
        # Test publishing
        await bus.publish_fact(fact_id1)
        # Test peers
        class MockPeer:
            async def receive_fact(self, fact):
                print(f"Peer received: {fact['fact']}")
        peer = MockPeer()
        bus.add_peer(peer)
        await bus.publish_fact(fact_id2)

    asyncio.run(test())