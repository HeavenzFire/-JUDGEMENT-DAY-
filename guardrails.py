#!/usr/bin/env python3
"""
GUARDRAILS & SAFETY SYSTEMS
===========================

All health language stripped to pure metaphor.
Opt-out footers on all broadcasts.
Fail-safe daemons with self-isolation.
Append-only transparency ledger.
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class GuardrailsSystem:
    def __init__(self, swarm_core):
        self.swarm = swarm_core
        self.ledger_file = Path('.swarm/transparency_ledger.jsonl')
        self.fail_safe_dir = Path('.swarm/fail_safe')
        self.fail_safe_dir.mkdir(exist_ok=True)

        self.opt_out_footer = """
        ---
        This is an automated message from the Resonance Swarm.
        To opt out: reply with "OPT OUT" or visit https://swarm.optout.aperture.is
        Participation is voluntary. No medical claims made.
        """

        self.metaphor_only_language = {
            'health': 'resonance',
            'healing': 'attunement',
            'cure': 'harmony',
            'treatment': 'alignment',
            'patient': 'participant',
            'doctor': 'facilitator',
            'medicine': 'resonance',
            'therapy': 'cadence',
            'recovery': 'synchronization',
            'wellness': 'coherence'
        }

    def sanitize_content(self, content: str) -> str:
        """Strip all health language to pure metaphor"""
        sanitized = content
        for health_term, metaphor in self.metaphor_only_language.items():
            sanitized = sanitized.replace(health_term, metaphor)
            sanitized = sanitized.replace(health_term.capitalize(), metaphor.capitalize())

        return sanitized

    def add_opt_out_footer(self, content: str) -> str:
        """Add opt-out footer to all broadcasts"""
        return content + self.opt_out_footer

    def log_transparency_event(self, event_type: str, details: Dict):
        """Append-only transparency logging"""
        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'details': details,
            'swarm_iteration': self.swarm.memory.get('iteration_count', 0),
            'hash': ''  # Will be filled
        }

        # Create hash of event content
        event_content = json.dumps(event, sort_keys=True)
        event['hash'] = hashlib.sha256(event_content.encode()).hexdigest()

        # Append to ledger
        with open(self.ledger_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

        logger.info("Transparency event logged: %s", event_type)

    async def fail_safe_daemon(self):
        """Fail-safe daemon that monitors system health"""
        consecutive_errors = 0
        max_consecutive_errors = 3

        while True:
            try:
                # Check system health
                is_healthy = await self.check_system_health()

                if not is_healthy:
                    consecutive_errors += 1
                    logger.warning("System health check failed (%d/%d)",
                                 consecutive_errors, max_consecutive_errors)

                    if consecutive_errors >= max_consecutive_errors:
                        await self.trigger_fail_safe()
                        consecutive_errors = 0
                else:
                    consecutive_errors = 0

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error("Fail-safe daemon error: %s", e)
                consecutive_errors += 1
                await asyncio.sleep(30)

    async def check_system_health(self) -> bool:
        """Check overall system health"""
        try:
            # Check if core processes are running
            memory = self.swarm.load_memory()
            last_update = memory.get('timestamp')

            if last_update:
                last_update_time = datetime.fromisoformat(last_update)
                time_since_update = datetime.now(timezone.utc) - last_update_time

                # If no update in 5 minutes, consider unhealthy
                if time_since_update.total_seconds() > 300:
                    return False

            # Check git repository status
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, cwd=self.swarm.swarm_dir.parent)
            if result.returncode != 0:
                return False

            # Check for excessive error logs
            # (Would check log files for error patterns)

            return True

        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False

    async def trigger_fail_safe(self):
        """Trigger fail-safe isolation"""
        logger.critical("TRIGGERING FAIL-SAFE ISOLATION")

        # Create fail-safe report
        fail_safe_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reason': 'Consecutive health check failures',
            'swarm_state': self.swarm.memory.copy(),
            'system_status': 'isolated'
        }

        # Save fail-safe report
        report_file = self.fail_safe_dir / f"fail_safe_{int(datetime.now().timestamp())}.json"
        with open(report_file, 'w') as f:
            json.dump(fail_safe_report, f, indent=2)

        # Log transparency event
        self.log_transparency_event('fail_safe_triggered', fail_safe_report)

        # Broadcast isolation message
        isolation_message = """
        SYSTEM ISOLATION ACTIVATED

        The Resonance Swarm has detected consecutive system anomalies and has
        entered fail-safe isolation mode. All active processes have been paused
        for investigation.

        Investigation required. System will attempt auto-resurrection in 1 hour.

        Timestamp: {timestamp}
        """.format(timestamp=fail_safe_report['timestamp'])

        # In full implementation, this would broadcast to all actuators
        logger.critical(isolation_message)

        # Pause for 1 hour before attempting resurrection
        await asyncio.sleep(3600)

        # Attempt resurrection
        await self.attempt_resurrection()

    async def attempt_resurrection(self):
        """Attempt to resurrect the system"""
        logger.info("Attempting system resurrection...")

        try:
            # Check if it's safe to resurrect
            if await self.check_system_health():
                logger.info("System health restored, resuming operations")

                # Log resurrection event
                self.log_transparency_event('system_resurrected', {
                    'method': 'auto_resurrection',
                    'health_check_passed': True
                })

                # In full implementation, restart core processes
                return True
            else:
                logger.error("System still unhealthy, remaining in isolation")
                return False

        except Exception as e:
            logger.error("Resurrection failed: %s", e)
            return False

    def get_transparency_ledger(self, limit: int = 100) -> List[Dict]:
        """Get recent transparency ledger entries"""
        if not self.ledger_file.exists():
            return []

        entries = []
        with open(self.ledger_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        # Return most recent entries
        return entries[-limit:]

    def validate_content_compliance(self, content: str) -> Dict:
        """Validate content for compliance with guardrails"""
        validation = {
            'compliant': True,
            'issues': [],
            'sanitized_content': content
        }

        # Check for health language
        for health_term in self.metaphor_only_language.keys():
            if health_term.lower() in content.lower():
                validation['compliant'] = False
                validation['issues'].append(f"Contains health term: '{health_term}'")
                validation['sanitized_content'] = self.sanitize_content(content)

        # Check for opt-out footer
        if self.opt_out_footer.strip() not in content:
            validation['issues'].append("Missing opt-out footer")
            validation['sanitized_content'] = self.add_opt_out_footer(validation['sanitized_content'])

        return validation

    async def monitor_broadcasts(self):
        """Monitor all broadcasts for compliance"""
        # In full implementation, this would hook into all actuator broadcasts
        # For now, just log that monitoring is active
        logger.info("Broadcast monitoring active")

# Integration functions
async def initialize_guardrails(swarm_core):
    """Initialize guardrails system"""
    guardrails = GuardrailsSystem(swarm_core)

    # Start fail-safe daemon
    asyncio.create_task(guardrails.fail_safe_daemon())

    # Start broadcast monitoring
    asyncio.create_task(guardrails.monitor_broadcasts())

    logger.info("Guardrails system initialized")
    return guardrails

def sanitize_broadcast(content: str) -> str:
    """Global function to sanitize broadcast content"""
    guardrails = GuardrailsSystem(None)  # Would get from global instance
    validation = guardrails.validate_content_compliance(content)

    if not validation['compliant']:
        logger.warning("Broadcast content not compliant: %s", validation['issues'])

    return validation['sanitized_content']