import asyncio
import hashlib
import json
from datetime import datetime

# === SEMANTIC BUS ===
class SemanticBus:
    def __init__(self):
        self.facts = {}  # key: fact_id, value: {fact, proof, scope, timestamp}
        self.subscribers = []

    def generate_proof(self, fact_data):
        # Simple SHA256 proof
        fact_str = json.dumps(fact_data, sort_keys=True)
        return hashlib.sha256(fact_str.encode()).hexdigest()

    async def publish_fact(self, fact, scope):
        timestamp = datetime.utcnow().isoformat()
        fact_data = {"fact": fact, "scope": scope, "timestamp": timestamp}
        proof = self.generate_proof(fact_data)
        fact_id = proof  # use proof as unique ID

        # Deduplicate
        if fact_id not in self.facts:
            self.facts[fact_id] = {**fact_data, "proof": proof}
            await self.notify_subscribers(self.facts[fact_id])

    async def notify_subscribers(self, fact_entry):
        for callback, subscribed_scope in self.subscribers:
            if subscribed_scope == fact_entry["scope"]:
                await callback(fact_entry)

    def subscribe(self, callback, scope):
        self.subscribers.append((callback, scope))

# === PRODUCER SERVICE ===
class ProducerService:
    def __init__(self, bus: SemanticBus):
        self.bus = bus

    async def run(self):
        i = 0
        while True:
            fact = {"temperature": 20 + i}
            await self.bus.publish_fact(fact, scope="environment")
            i = (i + 1) % 10
            await asyncio.sleep(3)  # publish every 3s

# === CONSUMER SERVICE ===
class ConsumerService:
    def __init__(self, bus: SemanticBus):
        self.bus = bus
        self.bus.subscribe(self.handle_fact, scope="environment")

    async def handle_fact(self, fact_entry):
        print(f"[Consumer] Received fact: {fact_entry}")

    async def run(self):
        # Keep the consumer alive
        while True:
            await asyncio.sleep(1)

# === MAIN ===
async def main():
    bus = SemanticBus()
    producer = ProducerService(bus)
    consumer = ConsumerService(bus)

    await asyncio.gather(
        producer.run(),
        consumer.run(),
    )

if __name__ == "__main__":
    asyncio.run(main())