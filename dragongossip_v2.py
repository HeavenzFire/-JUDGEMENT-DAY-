#!/usr/bin/env python3
# dragongossip_v2.py — Dragon Gossip v2.1 + Consensus Integration
# Deploy: systemctl enable --now dragon-gossip

import socket
import struct
import json
import time
import threading
import uuid
import logging
from typing import Dict, Callable
from dragon_gossip_v2_1_final import ContinuousConsensusModule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DRAGON_GOSSIP_V2 - %(levelname)s - %(message)s'
)
log = logging.getLogger("dragon_gossip_v2")

# === GOSSIP CONFIG ===
MCAST_GRP = "224.1.1.1"
MCAST_PORT = 5007
BROADCAST_RATE = 0.25  # 4Hz
PEER_TIMEOUT = 2.0
TTL = 2

class DragonGossipNode:
    def __init__(self):
        self.nodeid = str(uuid.uuid4())[:8]
        self.running = False
        self.peers: Dict[str, Dict] = {}
        self.local_state = {
            "syntropy": 0.5,
            "safety": "GREEN",
            "seq": 0,
            "ts": 0.0,
            "id": self.nodeid
        }
        
        # Consensus brain
        self.consensus = ContinuousConsensusModule(
            quorum_window=PEER_TIMEOUT,
            min_quorum=2,
            history_len=100
        )
        
        # Sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', TTL))
        
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_sock.bind(('', MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.recv_sock.settimeout(0.1)

    def update_local_syntropy(self, value: float, safety: str = "GREEN"):
        """Feed from your torsion/analytics engine"""
        self.local_state["syntropy"] = max(0.0, min(1.0, value))
        self.local_state["safety"] = safety

    def _broadcast_pulse(self):
        while self.running:
            try:
                self.local_state["seq"] += 1
                self.local_state["ts"] = time.time()
                payload = json.dumps(self.local_state).encode('utf-8')
                self.sock.sendto(payload, (MCAST_GRP, MCAST_PORT))
            except Exception as e:
                log.error(f"Broadcast error: {e}")
            time.sleep(BROADCAST_RATE)

    def _listen_pulse(self):
        while self.running:
            try:
                data, addr = self.recv_sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))
                
                # Timestamp fence (reject >250ms old)
                if time.time() - msg.get("ts", 0) > 0.25:
                    continue
                # Ignore self
                if msg.get("id") == self.nodeid:
                    continue
                
                self.peers[msg["id"]] = {
                    "syntropy": msg.get("syntropy", 0.0),
                    "safety": msg.get("safety", "RED"),
                    "last_seen": msg["ts"]
                }
            except socket.timeout:
                pass
            except Exception as e:
                log.error(f"Listener error: {e}")

    def _prune_peers(self):
        while self.running:
            now = time.time()
            dead = [nid for nid, data in self.peers.items() 
                   if now - data["last_seen"] > PEER_TIMEOUT]
            for nid in dead:
                log.debug(f"Peer {nid} timed out")
                del self.peers[nid]
            time.sleep(1.0)

    def start(self):
        self.running = True
        
        # Consensus callbacks
        def get_peer_state():
            return self.peers
        
        def get_local_state():
            return self.local_state.copy()
        
        # Start gossip threads
        threading.Thread(target=self._broadcast_pulse, daemon=True).start()
        threading.Thread(target=self._listen_pulse, daemon=True).start()
        threading.Thread(target=self._prune_peers, daemon=True).start()
        
        # Start consensus (non-blocking)
        self.consensus.run_continuous(get_peer_state, get_local_state, cycle_delay=0.25)
        
        log.info(f"🐉 Dragon Gossip v2.1 ONLINE: {self.nodeid} @ {MCAST_GRP}:{MCAST_PORT}")

    def stop(self):
        self.running = False
        self.consensus.stop()
        self.sock.close()
        self.recv_sock.close()
        log.info("🐉 Dragon Gossip OFFLINE")

    def snapshot(self):
        return {
            **self.consensus.snapshot(),
            "local_peers": len(self.peers),
            "local_syntropy": self.local_state["syntropy"]
        }

# === SYSTEMD SERVICE READY ===
if __name__ == "__main__":
    node = DragonGossipNode()
    
    # Simulate analytics feed
    def simulate_analytics():
        import random
        while node.running:
            node.update_local_syntropy(0.7 + random.uniform(-0.2, 0.2))
            print(f"📊 Swarm: {node.snapshot()}")
            time.sleep(1)
    
    node.start()
    threading.Thread(target=simulate_analytics, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.stop()