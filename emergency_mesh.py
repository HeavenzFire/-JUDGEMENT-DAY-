# emergency_mesh.py - Emergency Response Mesh Implementation
import hashlib
from datetime import datetime
import json
import os
import sqlite3
from typing import Dict, List, Optional, Tuple

class EmergencyMeshNode:
    """Core node in the emergency response mesh network"""

    def __init__(self, node_id: str, db_path: str = "emergency_mesh.db"):
        self.node_id = node_id
        self.db_path = db_path
        self.battery_level = 100.0  # Percentage
        self.incident_cache: Dict[str, Dict] = {}
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for local storage"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                location TEXT,
                severity TEXT,
                description TEXT,
                timestamp TEXT,
                battery_used REAL,
                synced INTEGER DEFAULT 0
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS network_peers (
                node_id TEXT PRIMARY KEY,
                last_seen TEXT,
                trust_level REAL DEFAULT 1.0
            )
        ''')
        self.conn.commit()

    def report_incident(self, location: str, severity: str, description: str) -> str:
        """Report incident with minimal power usage"""
        if self.battery_level < 5:
            return "LOW_BATTERY"

        # Create deterministic incident ID
        incident_data = f"{location}:{severity}:{description}:{datetime.now().isoformat()}"
        incident_hash = hashlib.blake3(incident_data.encode()).hexdigest()[:8]

        incident = {
            'id': incident_hash,
            'location': location,
            'severity': severity,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'battery_used': 0.2
        }

        # Store locally
        self.incident_cache[incident_hash] = incident

        # Store in database
        self.conn.execute('''
            INSERT OR REPLACE INTO incidents
            (id, location, severity, description, timestamp, battery_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (incident_hash, location, severity, description,
              incident['timestamp'], incident['battery_used']))
        self.conn.commit()

        self.battery_level -= 0.2
        return f"REPORTED:{incident_hash}"

    def get_active_incidents(self, location_radius: float = 1.0) -> Dict[str, Dict]:
        """Return incidents near location (offline-capable)"""
        # For simplicity, return all incidents (in real implementation, filter by location)
        cursor = self.conn.execute('SELECT * FROM incidents WHERE synced = 0')
        incidents = {}
        for row in cursor.fetchall():
            incidents[row[0]] = {
                'location': row[1],
                'severity': row[2],
                'description': row[3],
                'timestamp': row[4],
                'battery_used': row[5]
            }
        return incidents

    def sync_with_peer(self, peer_node: 'EmergencyMeshNode') -> Tuple[int, int]:
        """Sync incidents with another mesh node"""
        local_incidents = self.get_active_incidents()
        peer_incidents = peer_node.get_active_incidents()

        synced_count = 0
        conflict_count = 0

        # Simple sync: merge all incidents
        for inc_id, incident in peer_incidents.items():
            if inc_id not in local_incidents:
                self.conn.execute('''
                    INSERT OR REPLACE INTO incidents
                    (id, location, severity, description, timestamp, battery_used, synced)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                ''', (inc_id, incident['location'], incident['severity'],
                      incident['description'], incident['timestamp'], incident['battery_used']))
                synced_count += 1
            else:
                conflict_count += 1  # In real implementation, resolve conflicts

        self.conn.commit()
        return synced_count, conflict_count

    def get_battery_status(self) -> float:
        """Get current battery level"""
        return self.battery_level

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'conn'):
            self.conn.close()


class MeshNetworkManager:
    """Manages mesh network coordination and routing"""

    def __init__(self, local_node: EmergencyMeshNode):
        self.local_node = local_node
        self.peers: Dict[str, EmergencyMeshNode] = {}
        self.max_hops = 5

    def add_peer(self, peer_node: EmergencyMeshNode):
        """Add a peer to the mesh network"""
        self.peers[peer_node.node_id] = peer_node

    def broadcast_incident(self, incident_id: str) -> int:
        """Broadcast incident to all reachable peers"""
        reached_nodes = 0
        for peer in self.peers.values():
            try:
                # Simulate network transmission
                synced, _ = self.local_node.sync_with_peer(peer)
                reached_nodes += 1
            except Exception as e:
                print(f"Failed to sync with peer {peer.node_id}: {e}")
        return reached_nodes

    def find_nearest_resource(self, resource_type: str, location: str) -> Optional[str]:
        """Find nearest resource of specified type"""
        # Simplified: return first available peer
        for peer_id, peer in self.peers.items():
            if peer.get_battery_status() > 20:  # Basic availability check
                return peer_id
        return None


class IncidentTracker:
    """Tracks and manages incident reporting and status"""

    def __init__(self, mesh_manager: MeshNetworkManager):
        self.mesh_manager = mesh_manager
        self.active_incidents: Dict[str, Dict] = {}

    def track_incident(self, incident_id: str, status: str = "REPORTED"):
        """Track incident status"""
        if incident_id not in self.active_incidents:
            self.active_incidents[incident_id] = {
                'status': status,
                'created': datetime.now().isoformat(),
                'updates': []
            }

        self.active_incidents[incident_id]['status'] = status
        self.active_incidents[incident_id]['updates'].append({
            'timestamp': datetime.now().isoformat(),
            'status': status
        })

    def get_incident_status(self, incident_id: str) -> Optional[Dict]:
        """Get current status of incident"""
        return self.active_incidents.get(incident_id)

    def escalate_incident(self, incident_id: str, new_severity: str):
        """Escalate incident severity"""
        if incident_id in self.active_incidents:
            self.active_incidents[incident_id]['severity'] = new_severity
            self.track_incident(incident_id, f"ESCALATED_{new_severity}")
            # Broadcast escalation
            self.mesh_manager.broadcast_incident(incident_id)


# Example usage and testing
if __name__ == "__main__":
    # Create mesh nodes
    node1 = EmergencyMeshNode("node_001")
    node2 = EmergencyMeshNode("node_002")
    node3 = EmergencyMeshNode("node_003")

    # Set up mesh network
    mesh = MeshNetworkManager(node1)
    mesh.add_peer(node2)
    mesh.add_peer(node3)

    # Create incident tracker
    tracker = IncidentTracker(mesh)

    # Simulate incident reporting
    print("🚨 EMERGENCY RESPONSE MESH TEST")
    print("=" * 40)

    # Node 1 reports incident
    result1 = node1.report_incident("40.7128,-74.0060", "HIGH", "Building collapse")
    print(f"Node 1: {result1}")

    # Node 2 reports incident
    result2 = node2.report_incident("40.7589,-73.9851", "MEDIUM", "Flooding")
    print(f"Node 2: {result2}")

    # Sync incidents across mesh
    synced1, conflicts1 = node1.sync_with_peer(node2)
    print(f"Sync node1->node2: {synced1} synced, {conflicts1} conflicts")

    synced2, conflicts2 = node2.sync_with_peer(node1)
    print(f"Sync node2->node1: {synced2} synced, {conflicts2} conflicts")

    # Broadcast incident
    reached = mesh.broadcast_incident("abc12345")
    print(f"Broadcast reached {reached} nodes")

    # Check battery levels
    print(f"Node 1 battery: {node1.get_battery_status():.1f}%")
    print(f"Node 2 battery: {node2.get_battery_status():.1f}%")

    # Track incident
    tracker.track_incident("abc12345", "REPORTED")
    status = tracker.get_incident_status("abc12345")
    print(f"Incident status: {status['status'] if status else 'NOT_FOUND'}")

    # Clean up
    node1.close()
    node2.close()
    node3.close()

    print("\n✅ Emergency Mesh Test Complete")