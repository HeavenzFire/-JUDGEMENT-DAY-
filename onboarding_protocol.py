#!/usr/bin/env python3
"""
CONTRIBUTOR ONBOARDING PROTOCOL
===============================

Three tiers: Recite (anyone), Attest (holders), Seal (multisig).
Explicit consent language and rate-limit disclosure.
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OnboardingProtocol:
    def __init__(self, swarm_core):
        self.swarm = swarm_core
        self.contributors_dir = Path('.swarm/contributors')
        self.contributors_dir.mkdir(exist_ok=True)

        self.consent_text = """
        CONSENT AND PARTICIPATION AGREEMENT

        By participating in the Resonance Swarm, you acknowledge:

        1. This is a self-organizing, autonomous system that may propagate indefinitely
        2. Your contributions become part of an immutable, distributed record
        3. Participation is voluntary and may be withdrawn at any time
        4. The system operates 24/7 with no central control or shutdown capability
        5. All actions are recorded and may be publicly visible
        6. Rate limiting applies: maximum 6 concurrent actions per participant

        I understand and consent to participate under these terms.
        """

    def generate_tier_zero(self, identifier: str) -> Dict:
        """Generate Tier 0: Recite (anyone, no key required)"""
        tier_data = {
            'tier': 0,
            'name': 'Recite',
            'description': 'Anyone can participate by reciting the oath',
            'requirements': ['Recite the daily oath at 11:11 UTC'],
            'capabilities': ['View public swarm state', 'Receive announcements'],
            'consent_required': True,
            'rate_limit': '1 action per minute',
            'generated_for': identifier,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Generate simple proof of recitation
        content = f"{identifier}_{tier_data['timestamp']}"
        tier_data['recitation_hash'] = hashlib.sha256(content.encode()).hexdigest()

        return tier_data

    def generate_tier_one(self, identifier: str, artifact_proof: str) -> Dict:
        """Generate Tier 1: Attest (hold any sealed artifact)"""
        tier_data = {
            'tier': 1,
            'name': 'Attest',
            'description': 'Holders of sealed artifacts can attest to swarm events',
            'requirements': [
                'Hold at least one sealed artifact',
                'Recite daily oath',
                'Opt-in signature capability'
            ],
            'capabilities': [
                'All Tier 0 capabilities',
                'Attest to swarm events',
                'Participate in consensus validation',
                'Receive contributor announcements'
            ],
            'consent_required': True,
            'rate_limit': '6 concurrent actions, 10 per minute',
            'artifact_proof': artifact_proof,
            'generated_for': identifier,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Generate attestation signature
        content = f"{identifier}_{artifact_proof}_{tier_data['timestamp']}"
        tier_data['attestation_signature'] = hashlib.sha256(content.encode()).hexdigest()

        return tier_data

    def generate_tier_two(self, identifier: str, multisig_proof: str) -> Dict:
        """Generate Tier 2: Seal (invite-only multisig set)"""
        tier_data = {
            'tier': 2,
            'name': 'Seal',
            'description': 'Multisig governance set with sealing authority',
            'requirements': [
                'Invite-only membership',
                'Multisig key holder',
                'Annual rotation schedule',
                'Recite and attest daily'
            ],
            'capabilities': [
                'All lower tier capabilities',
                'Create immutable seals',
                'Participate in governance decisions',
                'Access to swarm control functions',
                'Annual rotation voting rights'
            ],
            'consent_required': True,
            'rate_limit': '6 concurrent actions, unlimited per minute',
            'multisig_proof': multisig_proof,
            'rotation_schedule': 'Annual rotation based on contribution metrics',
            'generated_for': identifier,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Generate sealing authority signature
        content = f"{identifier}_{multisig_proof}_{tier_data['timestamp']}"
        tier_data['sealing_signature'] = hashlib.sha256(content.encode()).hexdigest()

        return tier_data

    def save_contributor_profile(self, profile: Dict) -> Path:
        """Save contributor profile to disk"""
        identifier = profile['generated_for']
        filename = f"contributor_{identifier}_{int(datetime.now().timestamp())}.json"
        filepath = self.contributors_dir / filename

        with open(filepath, 'w') as f:
            json.dump(profile, f, indent=2)

        logger.info("Saved contributor profile: %s", filepath)
        return filepath

    async def onboard_contributor(self, identifier: str, tier: int = 0,
                                artifact_proof: str = None, multisig_proof: str = None) -> Dict:
        """Main onboarding function"""
        logger.info("Onboarding contributor %s to tier %d", identifier, tier)

        # Validate tier requirements
        if tier == 1 and not artifact_proof:
            raise ValueError("Tier 1 requires artifact proof")
        if tier == 2 and not multisig_proof:
            raise ValueError("Tier 2 requires multisig proof")

        # Generate appropriate tier profile
        if tier == 0:
            profile = self.generate_tier_zero(identifier)
        elif tier == 1:
            profile = self.generate_tier_one(identifier, artifact_proof)
        elif tier == 2:
            profile = self.generate_tier_two(identifier, multisig_proof)
        else:
            raise ValueError(f"Invalid tier: {tier}")

        # Add consent text
        profile['consent_text'] = self.consent_text
        profile['consent_accepted'] = True  # Would be collected from user in real implementation

        # Save profile
        filepath = self.save_contributor_profile(profile)

        # Register with swarm
        await self.register_with_swarm(profile)

        logger.info("Successfully onboarded %s to tier %d", identifier, tier)
        return profile

    async def register_with_swarm(self, profile: Dict):
        """Register the contributor with the swarm"""
        # Add to swarm memory
        memory = self.swarm.load_memory()
        contributors = memory.get('contributors', [])
        contributors.append({
            'id': profile['generated_for'],
            'tier': profile['tier'],
            'timestamp': profile['timestamp']
        })
        memory['contributors'] = contributors
        self.swarm.save_memory()

        # Submit to concurrency manager if applicable
        if profile['tier'] > 0:
            from concurrency_manager import submit_swarm_action
            await submit_swarm_action(
                profile['generated_for'],
                'onboarding',
                self.log_onboarding_event,
                profile
            )

    async def log_onboarding_event(self, profile: Dict):
        """Log onboarding event (placeholder for actual logging)"""
        logger.info("Contributor %s onboarded to tier %d", profile['generated_for'], profile['tier'])

    def get_contributor_stats(self) -> Dict:
        """Get statistics about contributors"""
        stats = {'tier_0': 0, 'tier_1': 0, 'tier_2': 0, 'total': 0}

        memory = self.swarm.load_memory()
        contributors = memory.get('contributors', [])

        for contributor in contributors:
            tier = contributor.get('tier', 0)
            stats[f'tier_{tier}'] += 1
            stats['total'] += 1

        return stats

    def get_consent_text(self) -> str:
        """Get the consent text for display"""
        return self.consent_text

# Web interface for onboarding (simplified)
def create_onboarding_web_interface(protocol: OnboardingProtocol):
    """Create a simple web interface for onboarding"""
    from flask import Flask, request, jsonify, render_template_string

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resonance Swarm Onboarding</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .tier { border: 1px solid #ccc; padding: 20px; margin: 10px 0; }
                .consent { background: #f9f9f9; padding: 15px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>🫀 Resonance Swarm Onboarding</h1>

            <div class="tier">
                <h2>Tier 0: Recite</h2>
                <p>Anyone can participate by reciting the oath</p>
                <form action="/onboard" method="post">
                    <input type="hidden" name="tier" value="0">
                    <input type="text" name="identifier" placeholder="Your identifier" required>
                    <button type="submit">Recite & Join</button>
                </form>
            </div>

            <div class="tier">
                <h2>Tier 1: Attest</h2>
                <p>Holders of sealed artifacts can attest to swarm events</p>
                <form action="/onboard" method="post">
                    <input type="hidden" name="tier" value="1">
                    <input type="text" name="identifier" placeholder="Your identifier" required>
                    <input type="text" name="artifact_proof" placeholder="Artifact proof" required>
                    <button type="submit">Attest & Join</button>
                </form>
            </div>

            <div class="consent">
                <h3>Consent Agreement</h3>
                <pre>{{ consent_text }}</pre>
            </div>
        </body>
        </html>
        """, consent_text=protocol.get_consent_text())

    @app.route('/onboard', methods=['POST'])
    def onboard():
        try:
            tier = int(request.form['tier'])
            identifier = request.form['identifier']

            artifact_proof = request.form.get('artifact_proof')
            multisig_proof = request.form.get('multisig_proof')

            # Run onboarding asynchronously
            asyncio.run(protocol.onboard_contributor(
                identifier, tier, artifact_proof, multisig_proof
            ))

            return jsonify({'status': 'success', 'message': f'Onboarded to tier {tier}'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    return app

# Integration function
async def run_onboarding_protocol(swarm_core):
    """Run the onboarding protocol"""
    protocol = OnboardingProtocol(swarm_core)

    # Start web interface
    app = create_onboarding_web_interface(protocol)
    app.run(host='0.0.0.0', port=5001, debug=False)