import asyncio
import datetime
import hashlib
import random
import time

# === QUANTUM SEMANTIC BUS ===
class QuantumSemanticBus:
    def __init__(self, node_id):
        self.node_id = node_id
        self.facts = {}
        self.peers = []

    def connect_peer(self, peer):
        if peer not in self.peers:
            self.peers.append(peer)

    async def notify_subscribers(self, fact):
        # Simulate notification
        print(f"[{datetime.datetime.utcnow().isoformat()}] [Node {self.node_id}] Notifying subscribers: {fact}")

    async def propagate_to_peers(self, fact):
        for peer in self.peers:
            await peer.receive_fact(fact)

    async def receive_fact(self, fact):
        fact_id = fact['proof']
        if fact_id not in self.facts:
            self.facts[fact_id] = fact
            print(f"[{datetime.datetime.utcnow().isoformat()}] [Node {self.node_id}] Received fact: {fact}")
            await self.notify_subscribers(fact)

# === QUANTUM PRODUCER SERVICE ===
class QuantumProducerService:
    def __init__(self, node):
        self.node = node
        self.running = False

    async def run(self):
        self.running = True
        while self.running:
            fact = {
                "fact": {"health_metric": random.randint(1, 100)},
                "scope": "life",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "node": self.node.node_id,
                "priority": 1.0,
                "proof": hashlib.sha256(f"fact_{time.time()}".encode()).hexdigest()
            }
            self.node.facts[fact['proof']] = fact
            await asyncio.sleep(1)

    def stop(self):
        self.running = False

# === CONSUMER SERVICE ===
class ConsumerService:
    def __init__(self, node, agent_name):
        self.node = node
        self.agent_name = agent_name

# === FACT RECLAMATION MIXIN ===
class FactReclamationMixin:
    async def reclaim_fact(self, fact_entry):
        """
        Re-propagate a fact flagged as lost or stolen.
        Priority boost simulates urgent recovery.
        """
        fact_id = fact_entry['proof']
        if fact_id not in self.facts:
            fact_copy = fact_entry.copy()
            fact_copy['priority'] += 0.5  # Boost for reclamation
            print(f"[{datetime.datetime.utcnow().isoformat()}] [Node {self.node_id}] Reclaiming fact: {fact_copy}")
            self.facts[fact_id] = fact_copy
            await self.notify_subscribers(fact_copy)
            await self.propagate_to_peers(fact_copy)

# === APPLY MIXIN TO QUANTUM SEMANTIC BUS ===
class ReclaimingQuantumBus(QuantumSemanticBus, FactReclamationMixin):
    pass

# === UPDATED PRODUCER AND CONSUMER USAGE ===
async def main_reclaim(run_duration: float = 10.0):
    nodes = [ReclaimingQuantumBus(node_id=n) for n in ['A', 'B', 'C']]
    for n in nodes:
        for peer in nodes:
            if peer != n:
                n.connect_peer(peer)

    producers = [QuantumProducerService(node) for node in nodes]
    consumers = [ConsumerService(node, agent_name=f'{node.node_id}-Agent') for node in nodes]

    tasks = [asyncio.create_task(p.run()) for p in producers]

    # Simulate a “stolen” fact
    await asyncio.sleep(1)
    stolen_fact = {
        "fact": {"health_metric": 999, "ethical_significance": 1.0},
        "scope": "life",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "node": "X",
        "priority": 1.0,
        "proof": hashlib.sha256(b"stolen_fact").hexdigest()
    }
    # Only Node A attempts to reclaim it
    await nodes[0].reclaim_fact(stolen_fact)

    await asyncio.sleep(run_duration)
    for p in producers:
        p.stop()
    await asyncio.gather(*tasks, return_exceptions=True)

def run_reclaim(run_duration: float = 10.0):
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            asyncio.create_task(main_reclaim(run_duration))
        else:
            asyncio.run(main_reclaim(run_duration))
    except RuntimeError:
        asyncio.run(main_reclaim(run_duration))

if __name__ == "__main__":
    run_reclaim()