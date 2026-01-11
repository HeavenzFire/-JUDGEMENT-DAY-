"""
Blockchain-Based Supply Chain Transparency System

Implements tamper-proof supply chain tracking to detect forced labor
and trafficking in global supply chains.

This addresses the critical challenge of hidden exploitation in
manufacturing and agricultural supply chains.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import random
import numpy as np
from dataclasses import dataclass, asdict
import uuid


@dataclass
class SupplyChainEvent:
    """Represents a single event in the supply chain"""
    event_id: str
    timestamp: str
    event_type: str  # 'harvested', 'processed', 'manufactured', 'shipped', 'inspected'
    location: Dict[str, float]  # {'lat': float, 'lng': float}
    actor_id: str  # Worker, machine, or facility ID
    product_batch_id: str
    quantity: float
    unit: str  # 'kg', 'pieces', 'liters', etc.
    metadata: Dict[str, Any]  # Additional event data
    previous_event_hash: str = ""
    event_hash: str = ""

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the event data"""
        # Convert location coordinates to strings for consistent hashing
        location_str = f"{self.location['lat']:.6f},{self.location['lng']:.6f}"

        event_data = {
            'event_id': self.event_id,
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'location': location_str,
            'actor_id': self.actor_id,
            'product_batch_id': self.product_batch_id,
            'quantity': self.quantity,
            'unit': self.unit,
            'metadata': json.dumps(self.metadata, sort_keys=True),
            'previous_event_hash': self.previous_event_hash
        }

        # Create deterministic JSON string
        json_str = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode()).hexdigest()

    def sign_event(self) -> None:
        """Sign the event with its hash"""
        self.event_hash = self.calculate_hash()


@dataclass
class ProductBatch:
    """Represents a batch of products being tracked"""
    batch_id: str
    product_type: str
    origin_location: Dict[str, float]
    creation_timestamp: str
    initial_quantity: float
    unit: str
    supply_chain_events: List[SupplyChainEvent] = None
    current_quantity: float = 0
    status: str = "active"  # 'active', 'completed', 'flagged', 'seized'

    def __post_init__(self):
        if self.supply_chain_events is None:
            self.supply_chain_events = []
        self.current_quantity = self.initial_quantity


class WorkerVerification:
    """Handles worker identity verification and consent tracking"""

    def __init__(self):
        self.verified_workers = {}  # worker_id -> verification_data
        self.consent_records = {}   # worker_id -> consent_hash

    def verify_worker(self, worker_id: str, verification_data: Dict[str, Any]) -> bool:
        """Verify worker identity and working conditions"""
        # In production, this would integrate with government ID systems
        # and biometric verification

        required_fields = ['name', 'age', 'location', 'consent_given', 'working_conditions']

        if not all(field in verification_data for field in required_fields):
            return False

        # Check age (no child labor)
        if verification_data['age'] < 18:
            return False

        # Check consent
        if not verification_data['consent_given']:
            return False

        # Check working conditions
        conditions = verification_data['working_conditions']
        if not self._validate_working_conditions(conditions):
            return False

        # Store verification
        self.verified_workers[worker_id] = {
            'verification_data': verification_data,
            'verification_timestamp': datetime.now().isoformat(),
            'verification_hash': self._hash_verification_data(verification_data)
        }

        return True

    def _validate_working_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Validate that working conditions meet minimum standards"""
        # Check for forced labor indicators
        if conditions.get('freedom_of_movement', False) == False:
            return False

        if conditions.get('debt_bondage', False) == True:
            return False

        if conditions.get('adequate_pay', False) == False:
            return False

        if conditions.get('safe_environment', False) == False:
            return False

        return True

    def _hash_verification_data(self, data: Dict[str, Any]) -> str:
        """Create hash of verification data for integrity"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def record_consent(self, worker_id: str, consent_details: Dict[str, Any]) -> str:
        """Record worker consent for supply chain participation"""
        consent_data = {
            'worker_id': worker_id,
            'consent_given': True,
            'consent_timestamp': datetime.now().isoformat(),
            'consent_details': consent_details,
            'consent_hash': self._hash_verification_data(consent_details)
        }

        self.consent_records[worker_id] = consent_data
        return consent_data['consent_hash']


class SupplyChainTracker:
    """
    Main blockchain-based supply chain tracking system
    """

    def __init__(self):
        self.batches = {}  # batch_id -> ProductBatch
        self.worker_verifier = WorkerVerification()
        self.blockchain = []  # Simple list for demo; in production would be distributed
        self.risk_indicators = self._initialize_risk_indicators()

    def _initialize_risk_indicators(self) -> Dict[str, Any]:
        """Initialize risk detection patterns"""
        return {
            'quantity_anomalies': {
                'sudden_drops': 0.3,  # 30% drop threshold
                'unexplained_gains': 0.2  # 20% gain threshold
            },
            'location_anomalies': {
                'distance_threshold_km': 5000,  # Flag if batch moves too far too fast
                'time_threshold_hours': 24
            },
            'worker_concentration': {
                'max_workers_per_batch': 50,  # Flag if too many workers on one batch
                'min_workers_per_batch': 3
            },
            'processing_time_anomalies': {
                'min_processing_hours': 1,
                'max_processing_hours': 720  # 30 days
            }
        }

    def create_batch(self, product_type: str, origin_location: Dict[str, float],
                    initial_quantity: float, unit: str) -> str:
        """Create a new product batch for tracking"""
        batch_id = str(uuid.uuid4())

        batch = ProductBatch(
            batch_id=batch_id,
            product_type=product_type,
            origin_location=origin_location,
            creation_timestamp=datetime.now().isoformat(),
            initial_quantity=initial_quantity,
            unit=unit
        )

        self.batches[batch_id] = batch

        # Create initial event
        initial_event = SupplyChainEvent(
            event_id=str(uuid.uuid4()),
            timestamp=batch.creation_timestamp,
            event_type="batch_created",
            location=origin_location,
            actor_id="system",
            product_batch_id=batch_id,
            quantity=initial_quantity,
            unit=unit,
            metadata={"batch_creation": True}
        )
        initial_event.sign_event()

        batch.supply_chain_events.append(initial_event)
        self._add_to_blockchain(initial_event)

        return batch_id

    def add_supply_chain_event(self, batch_id: str, event_type: str,
                             location: Dict[str, float], actor_id: str,
                             quantity_change: float, metadata: Dict[str, Any] = None) -> bool:
        """Add a new event to the supply chain"""
        if batch_id not in self.batches:
            return False

        batch = self.batches[batch_id]
        if metadata is None:
            metadata = {}

        # Get previous event hash
        previous_hash = ""
        if batch.supply_chain_events:
            previous_hash = batch.supply_chain_events[-1].event_hash

        # Create new event
        event = SupplyChainEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            location=location,
            actor_id=actor_id,
            product_batch_id=batch_id,
            quantity=quantity_change,
            unit=batch.unit,
            metadata=metadata,
            previous_event_hash=previous_hash
        )
        event.sign_event()

        # Update batch quantity
        if event_type in ['harvested', 'processed', 'manufactured']:
            batch.current_quantity += quantity_change
        elif event_type in ['shipped', 'sold']:
            batch.current_quantity -= abs(quantity_change)

        # Validate event doesn't create negative quantity
        if batch.current_quantity < 0:
            return False

        batch.supply_chain_events.append(event)
        self._add_to_blockchain(event)

        # Check for risk indicators
        risk_flags = self._analyze_risks(batch, event)
        if risk_flags:
            batch.status = "flagged"
            metadata['risk_flags'] = risk_flags

        return True

    def _add_to_blockchain(self, event: SupplyChainEvent) -> None:
        """Add event to blockchain (simplified for demo)"""
        block = {
            'event_hash': event.event_hash,
            'event_data': asdict(event),
            'block_timestamp': datetime.now().isoformat(),
            'previous_block_hash': self.blockchain[-1]['event_hash'] if self.blockchain else "genesis"
        }
        block['block_hash'] = hashlib.sha256(
            json.dumps(block, sort_keys=True).encode()
        ).hexdigest()

        self.blockchain.append(block)

    def _analyze_risks(self, batch: ProductBatch, new_event: SupplyChainEvent) -> List[str]:
        """Analyze supply chain events for risk indicators"""
        risks = []

        # Quantity anomaly detection
        if len(batch.supply_chain_events) >= 2:
            prev_quantity = batch.supply_chain_events[-2].quantity
            quantity_change_pct = abs(new_event.quantity - prev_quantity) / max(1, prev_quantity)

            if quantity_change_pct > self.risk_indicators['quantity_anomalies']['sudden_drops']:
                risks.append("sudden_quantity_drop")

        # Location anomaly detection
        if len(batch.supply_chain_events) >= 2:
            prev_location = batch.supply_chain_events[-2].location
            distance = self._calculate_distance(prev_location, new_event.location)

            # Simple distance check (in production, use proper geospatial calculations)
            if distance > self.risk_indicators['location_anomalies']['distance_threshold_km']:
                risks.append("impossible_location_jump")

        # Worker concentration check
        worker_counts = {}
        for event in batch.supply_chain_events[-10:]:  # Last 10 events
            worker_counts[event.actor_id] = worker_counts.get(event.actor_id, 0) + 1

        if len(worker_counts) < self.risk_indicators['worker_concentration']['min_workers_per_batch']:
            risks.append("insufficient_worker_diversity")

        if len(worker_counts) > self.risk_indicators['worker_concentration']['max_workers_per_batch']:
            risks.append("excessive_worker_concentration")

        return risks

    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate approximate distance between two points (in km)"""
        # Simplified Haversine formula approximation
        lat1, lng1 = loc1['lat'], loc1['lng']
        lat2, lng2 = loc2['lat'], loc2['lng']

        dlat = abs(lat2 - lat1)
        dlng = abs(lng2 - lng1)

        # Rough approximation: 111 km per degree latitude, 111 * cos(lat) per degree longitude
        lat_km = dlat * 111
        lng_km = dlng * 111 * np.cos(np.radians((lat1 + lat2) / 2))

        return np.sqrt(lat_km**2 + lng_km**2)

    def verify_worker_participation(self, batch_id: str, worker_id: str,
                                  verification_data: Dict[str, Any]) -> bool:
        """Verify worker participation in supply chain"""
        if not self.worker_verifier.verify_worker(worker_id, verification_data):
            return False

        # Add verification event to batch
        verification_event = SupplyChainEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            event_type="worker_verified",
            location=verification_data.get('location', {'lat': 0, 'lng': 0}),
            actor_id=worker_id,
            product_batch_id=batch_id,
            quantity=0,  # No quantity change
            unit="workers",
            metadata={
                'verification_type': 'worker_conditions',
                'consent_hash': self.worker_verifier.consent_records.get(worker_id, {}).get('consent_hash')
            }
        )

        if batch_id in self.batches:
            batch = self.batches[batch_id]
            verification_event.previous_event_hash = batch.supply_chain_events[-1].event_hash if batch.supply_chain_events else ""
            verification_event.sign_event()
            batch.supply_chain_events.append(verification_event)
            self._add_to_blockchain(verification_event)

        return True

    def audit_batch(self, batch_id: str) -> Dict[str, Any]:
        """Audit a product batch for compliance and risks"""
        if batch_id not in self.batches:
            return {"error": "Batch not found"}

        batch = self.batches[batch_id]

        audit_results = {
            'batch_id': batch_id,
            'product_type': batch.product_type,
            'status': batch.status,
            'total_events': len(batch.supply_chain_events),
            'current_quantity': batch.current_quantity,
            'quantity_loss': batch.initial_quantity - batch.current_quantity,
            'risk_flags': [],
            'compliance_score': 100,  # Start at perfect
            'recommendations': []
        }

        # Analyze event chain integrity
        if not self._verify_event_chain_integrity(batch):
            audit_results['risk_flags'].append("chain_integrity_broken")
            audit_results['compliance_score'] -= 30

        # Check for worker verification
        verified_workers = set()
        for event in batch.supply_chain_events:
            if event.event_type == "worker_verified":
                verified_workers.add(event.actor_id)

        if len(verified_workers) == 0:
            audit_results['risk_flags'].append("no_worker_verification")
            audit_results['compliance_score'] -= 40
            audit_results['recommendations'].append("Conduct worker verification audit")

        # Check for risk flags in events
        for event in batch.supply_chain_events:
            if 'risk_flags' in event.metadata:
                audit_results['risk_flags'].extend(event.metadata['risk_flags'])

        # Deduct points for each risk flag
        unique_risks = set(audit_results['risk_flags'])
        audit_results['compliance_score'] -= len(unique_risks) * 10

        # Ensure score doesn't go below 0
        audit_results['compliance_score'] = max(0, audit_results['compliance_score'])

        # Generate final recommendations
        if audit_results['compliance_score'] < 50:
            audit_results['recommendations'].append("URGENT: Comprehensive audit required")
        elif audit_results['compliance_score'] < 80:
            audit_results['recommendations'].append("Monitor closely and address risk flags")

        return audit_results

    def _verify_event_chain_integrity(self, batch: ProductBatch) -> bool:
        """Verify that the event chain hasn't been tampered with"""
        for i, event in enumerate(batch.supply_chain_events):
            # Recalculate hash and compare
            expected_hash = event.calculate_hash()
            if expected_hash != event.event_hash:
                return False

            # Check chain linkage
            if i > 0:
                if event.previous_event_hash != batch.supply_chain_events[i-1].event_hash:
                    return False

        return True

    def get_batch_traceability_report(self, batch_id: str) -> Dict[str, Any]:
        """Generate complete traceability report for a batch"""
        if batch_id not in self.batches:
            return {"error": "Batch not found"}

        batch = self.batches[batch_id]

        report = {
            'batch_info': {
                'batch_id': batch.batch_id,
                'product_type': batch.product_type,
                'origin': batch.origin_location,
                'created': batch.creation_timestamp,
                'initial_quantity': batch.initial_quantity,
                'current_quantity': batch.current_quantity,
                'status': batch.status
            },
            'supply_chain_events': [
                {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp,
                    'type': event.event_type,
                    'location': event.location,
                    'actor': event.actor_id,
                    'quantity_change': event.quantity,
                    'metadata': event.metadata
                }
                for event in batch.supply_chain_events
            ],
            'blockchain_integrity': self._verify_event_chain_integrity(batch),
            'audit_results': self.audit_batch(batch_id)
        }

        return report


def demonstrate_supply_chain_tracking():
    """Demonstrate the blockchain supply chain tracking system"""
    print("⛓️ BLOCKCHAIN SUPPLY CHAIN TRANSPARENCY SYSTEM")
    print("=" * 60)

    tracker = SupplyChainTracker()

    # Create a product batch
    print("Creating coffee bean batch...")
    batch_id = tracker.create_batch(
        product_type="coffee_beans",
        origin_location={'lat': -1.2921, 'lng': 36.8219},  # Nairobi, Kenya
        initial_quantity=1000.0,
        unit="kg"
    )
    print(f"Created batch: {batch_id}")

    # Add harvesting event
    print("\nAdding harvesting event...")
    tracker.add_supply_chain_event(
        batch_id=batch_id,
        event_type="harvested",
        location={'lat': -1.2921, 'lng': 36.8219},
        actor_id="worker_001",
        quantity_change=1000.0,
        metadata={"farm_id": "FARM_001", "certification": "fair_trade"}
    )

    # Verify worker
    print("Verifying worker participation...")
    worker_verification = {
        'name': 'Maria Gonzalez',
        'age': 28,
        'location': {'lat': -1.2921, 'lng': 36.8219},
        'consent_given': True,
        'working_conditions': {
            'freedom_of_movement': True,
            'debt_bondage': False,
            'adequate_pay': True,
            'safe_environment': True
        }
    }

    tracker.verify_worker_participation(batch_id, "worker_001", worker_verification)

    # Add processing event
    print("Adding processing event...")
    tracker.add_supply_chain_event(
        batch_id=batch_id,
        event_type="processed",
        location={'lat': -1.2833, 'lng': 36.8167},  # Processing facility
        actor_id="facility_001",
        quantity_change=-50.0,  # 50kg waste/loss
        metadata={"process_type": "roasting", "quality_check": "passed"}
    )

    # Add shipping event
    print("Adding shipping event...")
    tracker.add_supply_chain_event(
        batch_id=batch_id,
        event_type="shipped",
        location={'lat': 40.7128, 'lng': -74.0060},  # New York
        actor_id="shipping_co_001",
        quantity_change=-950.0,  # Shipped remaining 950kg
        metadata={"destination": "New York", "shipping_method": "container_ship"}
    )

    # Generate traceability report
    print("\nGenerating traceability report...")
    report = tracker.get_batch_traceability_report(batch_id)

    print(f"Batch Status: {report['batch_info']['status']}")
    print(f"Total Events: {len(report['supply_chain_events'])}")
    print(f"Blockchain Integrity: {report['blockchain_integrity']}")
    print(f"Audit Compliance Score: {report['audit_results']['compliance_score']}%")

    if report['audit_results']['risk_flags']:
        print(f"Risk Flags: {report['audit_results']['risk_flags']}")

    print("\n✅ Blockchain supply chain tracking operational!")
    print("This system provides tamper-proof tracking of products from origin to consumer,")
    print("enabling detection of forced labor and trafficking in global supply chains.")


if __name__ == "__main__":
    demonstrate_supply_chain_tracking()