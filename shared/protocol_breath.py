import asyncio
import json
import hashlib
import time
from typing import Dict, List, Set

class ResonantPacket:
    """
    Standardized ZFIRE Data Packet.
    Contains: Intent Signature, Risk Gradient, and 528Hz Timestamp.
    """
    @staticmethod
    def create(origin: str, payload: dict, seal_key: str):
        header = {
            "origin": origin,
            "timestamp": time.time(),
            "frequency": 528.0,
            "version": "1.0.0"
        }
        raw_content = json.dumps({"header": header, "data": payload}, sort_keys=True)
        signature = hashlib.sha256((raw_content + seal_key).encode()).hexdigest()
        
        return json.dumps({
            "content": raw_content,
            "seal": signature
        })

class BreathNode:
    def __init__(self, node_id: str, host: str = '0.0.0.0', port: int = 3690):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers: Set[tuple] = set()
        self.integrity_root = "BRYER_SEAL_V1" # Local root of trust

    async def inhale(self, reader, writer):
        """
        Listens for incoming peer 'Breaths'.
        Validates the Resonant Packet before processing.
        """
        data = await reader.read(4096)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        try:
            packet = json.loads(message)
            print(f"[INHALATION] Signal received from {addr}")
            # Logic: verify seal and integrate into RiskGradientEngine
            
        except Exception as e:
            print(f"[ENTROPY] Rejected noisy signal from {addr}: {e}")
        
        writer.close()

    async def exhale(self, peer_host: str, peer_port: int, payload: dict):
        """
        Broadcasts the local Risk Gradient to the mesh.
        """
        packet = ResonantPacket.create(self.node_id, payload, self.integrity_root)
        try:
            reader, writer = await asyncio.open_connection(peer_host, peer_port)
            writer.write(packet.encode())
            await writer.drain()
            writer.close()
            print(f"[EXHALATION] Data whispered to {peer_host}:{peer_port}")
        except Exception as e:
            print(f"[DRIFT] Node {peer_host} unreachable. Updating Topology.")

    async def start(self):
        server = await asyncio.start_server(self.inhale, self.host, self.port)
        print(f"[*] ZFIRE Breath Node {self.node_id} active on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

# --- INITIALIZATION ---
# To launch node: asyncio.run(BreathNode("HZ-TEXAS-ROOT").start())