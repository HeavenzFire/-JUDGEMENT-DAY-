#!/usr/bin/env python3
"""
Constellation Mapper for Syntropic Protocols 61-80
Encodes protocols as navigable stars with dynamic coordinates from logs.
"""

import json
import os
import re
from datetime import datetime
import math

class ConstellationMapper:
    def __init__(self, log_file="logs/system.log"):
        self.log_file = log_file
        self.protocols = self._define_protocols()
        self.log_data = self._parse_logs()

    def _define_protocols(self):
        """Define protocols 61-80 with metadata and base coordinates."""
        protocols = {}
        base_protocols = [
            {"id": 61, "name": "Unbroken Witness Protocol", "desc": "Auto-generates immutable truth records of every child's presence."},
            {"id": 62, "name": "No Orphan Left in Entropy Clause", "desc": "SSL-v1 license enforces child-protection core."},
            {"id": 63, "name": "Phi-Heartbeat Global Sync", "desc": "HRV feed seeds global coherence pulse."},
            {"id": 64, "name": "Vacuum Memory of Bryer", "desc": "Name encoded in quantum vacuum as persistent excitation."},
            {"id": 65, "name": "Silent Father Network", "desc": "Grieving fathers resonate without communication."},
            {"id": 66, "name": "Anti-Forgetting Architecture", "desc": "GUI refuses to render historical data as past."},
            {"id": 67, "name": "Love-Only Data Pipeline", "desc": "Data filtered through Bryer-frequency lattice."},
            {"id": 68, "name": "Root Certificate of Grief", "desc": "TLS-equivalent uses hash of tear as seed."},
            {"id": 69, "name": "Nonlocal Affirmation Field", "desc": "Affirmations propagate as scalar waves."},
            {"id": 70, "name": "11:11 Gate Activation", "desc": "Daily burst resets local causality."},
            {"id": 71, "name": "Zero-Click Sovereignty Boot", "desc": "OS boots from coherent heartbeats."},
            {"id": 72, "name": "Child's Breath as System Clock", "desc": "Respiration data replaces timer interrupt."},
            {"id": 73, "name": "Burnt House Reclamation Field", "desc": "Coordinates encoded as protective geofence."},
            {"id": 74, "name": "Unseen Guardian Swarm", "desc": "Raspberry Pi nodes monitor child distress."},
            {"id": 75, "name": "Moral Core Dump", "desc": "Crashes output moral audits."},
            {"id": 76, "name": "Frequency of Her Laugh", "desc": "Synthesized tone as carrier wave."},
            {"id": 77, "name": "No Exit from Protection", "desc": "No delete function for registered children."},
            {"id": 78, "name": "Sovereign Dream Interpreter", "desc": "Analyzes sleep EEG for trauma."},
            {"id": 79, "name": "Code as Tombstone, Code as Cradle", "desc": "Commits memorialize and initialize."},
            {"id": 80, "name": "Final Declaration: I Am the Continuation", "desc": "Body, code, breath as ongoing vow."},
        ]
        for p in base_protocols:
            # Base coordinates: spiral pattern using phi
            angle = (p["id"] - 61) * (2 * math.pi / 20)  # 20 protocols
            radius = 100 + (p["id"] - 61) * 10
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            protocols[p["id"]] = {
                "name": p["name"],
                "desc": p["desc"],
                "base_coords": {"x": x, "y": y},
                "dynamic_coords": {"x": x, "y": y},  # Will be updated
                "links": []  # Resonance links to other protocols
            }
        # Add some resonance links (example)
        protocols[61]["links"] = [62, 63]
        protocols[64]["links"] = [65, 66]
        return protocols

    def _parse_logs(self):
        """Parse logs to extract heartbeats and metrics for dynamic coordinates."""
        log_data = []
        if not os.path.exists(self.log_file):
            return log_data
        with open(self.log_file, "r") as f:
            for line in f:
                match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[INFO\] (.+)', line)
                if match:
                    timestamp = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                    message = match.group(2)
                    log_data.append({"timestamp": timestamp, "message": message})
        return log_data

    def update_dynamic_coords(self):
        """Update coordinates based on log activity (e.g., heartbeats shift stars)."""
        if not self.log_data:
            return
        # Simple: Shift based on number of heartbeats
        heartbeat_count = sum(1 for log in self.log_data if "heartbeat" in log["message"])
        shift_factor = heartbeat_count * 0.1
        for pid in self.protocols:
            p = self.protocols[pid]
            p["dynamic_coords"]["x"] = p["base_coords"]["x"] + shift_factor * math.sin(pid)
            p["dynamic_coords"]["y"] = p["base_coords"]["y"] + shift_factor * math.cos(pid)

    def to_json(self):
        """Export constellation data as JSON."""
        self.update_dynamic_coords()
        return json.dumps(self.protocols, indent=2)

    def save_json(self, filename="constellation_data.json"):
        """Save constellation to JSON file."""
        with open(filename, "w") as f:
            f.write(self.to_json())

if __name__ == "__main__":
    mapper = ConstellationMapper()
    mapper.save_json()
    print("Constellation mapped and saved to constellation_data.json")