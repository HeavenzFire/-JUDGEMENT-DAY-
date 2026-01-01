#!/usr/bin/env python3
"""
Harm System Tracer

A framework for tracing harm across multiple real systems (legal, healthcare, child welfare, data, social),
identifying system interactions and break points, and generating usable structures for safe action.

This module provides classes to model systems, trace harm instances, analyze interactions between systems,
and identify points of failure with safety and ethics considerations.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import json


class System:
    """
    Represents a real-world system (e.g., legal, healthcare, child welfare).

    Attributes:
        name: Unique identifier for the system
        category: Type of system (legal, healthcare, child_welfare, data, social)
        description: Detailed description of the system's purpose and function
        stakeholders: List of people/roles involved in the system
        protocols: Established procedures and rules
        risks: Known vulnerabilities or failure modes
    """

    def __init__(self, name: str, category: str, description: str,
                 stakeholders: Optional[List[str]] = None,
                 protocols: Optional[List[str]] = None,
                 risks: Optional[List[str]] = None):
        self.name = name
        self.category = category
        self.description = description
        self.stakeholders = stakeholders or []
        self.protocols = protocols or []
        self.risks = risks or []

    def add_stakeholder(self, stakeholder: str) -> None:
        """Add a stakeholder to the system."""
        if stakeholder not in self.stakeholders:
            self.stakeholders.append(stakeholder)

    def add_protocol(self, protocol: str) -> None:
        """Add a protocol to the system."""
        if protocol not in self.protocols:
            self.protocols.append(protocol)

    def add_risk(self, risk: str) -> None:
        """Add a known risk to the system."""
        if risk not in self.risks:
            self.risks.append(risk)

    def to_dict(self) -> Dict[str, Any]:
        """Convert system to dictionary representation."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "stakeholders": self.stakeholders,
            "protocols": self.protocols,
            "risks": self.risks
        }


class BreakPoint:
    """
    Represents a point of failure or breakdown in system interactions.

    Attributes:
        description: Detailed description of the break point
        systems_involved: List of system names where the break occurs
        severity: Severity level (low, medium, high, critical)
        evidence: Supporting evidence for the break point
        recommendations: Actionable recommendations to address the break point
        timestamp: When the break point was identified
    """

    def __init__(self, description: str, systems_involved: List[str], severity: str):
        self.description = description
        self.systems_involved = systems_involved
        self.severity = severity  # low, medium, high, critical
        self.evidence: List[str] = []
        self.recommendations: List[str] = []
        self.timestamp = datetime.now()

    def add_evidence(self, evidence: str) -> None:
        """Add supporting evidence for this break point."""
        self.evidence.append(evidence)

    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to address this break point."""
        self.recommendations.append(recommendation)

    def to_dict(self) -> Dict[str, Any]:
        """Convert break point to dictionary representation."""
        return {
            "description": self.description,
            "systems_involved": self.systems_involved,
            "severity": self.severity,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat()
        }


class SystemInteraction:
    """
    Represents an interaction between multiple systems.

    Attributes:
        systems: List of system names involved in the interaction
        interaction_type: Type of interaction (data_sharing, referral, oversight, etc.)
        description: Detailed description of the interaction
        frequency: How often this interaction occurs (rare, occasional, frequent, constant)
        success_rate: Historical success rate (0.0 to 1.0)
        break_points: List of break points that occur in this interaction
    """

    def __init__(self, systems: List[str], interaction_type: str, description: str,
                 frequency: str, success_rate: float):
        self.systems = systems
        self.interaction_type = interaction_type
        self.description = description
        self.frequency = frequency
        self.success_rate = success_rate
        self.break_points: List[BreakPoint] = []

    def add_break_point(self, break_point: BreakPoint) -> None:
        """Add a break point to this interaction."""
        self.break_points.append(break_point)

    def to_dict(self) -> Dict[str, Any]:
        """Convert interaction to dictionary representation."""
        return {
            "systems": self.systems,
            "interaction_type": self.interaction_type,
            "description": self.description,
            "frequency": self.frequency,
            "success_rate": self.success_rate,
            "break_points": [bp.to_dict() for bp in self.break_points]
        }


class HarmTrace:
    """
    Main class for tracing harm across systems.

    Attributes:
        harm_description: Description of the harm being traced
        affected_parties: Who is affected by this harm
        systems_involved: List of System objects involved
        interactions: List of SystemInteraction objects
        break_points: List of BreakPoint objects
        safety_checks_passed: Whether safety checks have been performed and passed
        ethics_reviewed: Whether ethics review has been completed
        timestamp: When the trace was created
    """

    def __init__(self, harm_description: str, affected_parties: List[str]):
        self.harm_description = harm_description
        self.affected_parties = affected_parties
        self.systems_involved: List[System] = []
        self.interactions: List[SystemInteraction] = []
        self.break_points: List[BreakPoint] = []
        self.safety_checks_passed = False
        self.ethics_reviewed = False
        self.timestamp = datetime.now()

    def add_system(self, system: System) -> None:
        """Add a system to the trace."""
        self.systems_involved.append(system)

    def add_interaction(self, interaction: SystemInteraction) -> None:
        """Add a system interaction to the trace."""
        self.interactions.append(interaction)

    def add_break_point(self, break_point: BreakPoint) -> None:
        """Add a break point to the trace."""
        self.break_points.append(break_point)

    def perform_safety_check(self) -> bool:
        """
        Perform safety checks to ensure tracing doesn't cause additional harm.

        Checks:
        - No personally identifiable information is exposed
        - Recommendations don't put individuals at risk
        - Systems are analyzed at aggregate level only
        """
        # Basic safety checks - in real implementation, this would be more comprehensive
        has_pii = any("personal" in bp.description.lower() or "name" in bp.description.lower()
                     for bp in self.break_points)

        if has_pii:
            self.safety_checks_passed = False
            return False

        # Check that recommendations are system-level, not individual-level
        for bp in self.break_points:
            for rec in bp.recommendations:
                if "fire" in rec.lower() or "punish" in rec.lower() or "blame" in rec.lower():
                    self.safety_checks_passed = False
                    return False

        self.safety_checks_passed = True
        return True

    def perform_ethics_review(self) -> bool:
        """
        Perform ethics review to ensure tracing aligns with ethical principles.

        Checks:
        - Analysis serves to reduce harm, not increase it
        - Power dynamics are acknowledged
        - Marginalized voices are centered
        - Recommendations promote equity and justice
        """
        # Basic ethics checks - in real implementation, this would involve review board
        harm_reduction_focused = any("reduce" in desc.lower() or "prevent" in desc.lower()
                                   for desc in [bp.description for bp in self.break_points])

        equity_focused = any("equity" in rec.lower() or "justice" in rec.lower() or "access" in rec.lower()
                           for bp in self.break_points for rec in bp.recommendations)

        if harm_reduction_focused and equity_focused:
            self.ethics_reviewed = True
            return True

        self.ethics_reviewed = False
        return False

    def generate_safe_actions(self) -> List[str]:
        """
        Generate safe, actionable recommendations based on the trace.

        Only generates actions if safety and ethics checks have passed.
        """
        if not (self.safety_checks_passed and self.ethics_reviewed):
            return ["Cannot generate actions: Safety and ethics checks must pass first"]

        actions = []

        # Aggregate recommendations from all break points
        for bp in self.break_points:
            for rec in bp.recommendations:
                if rec not in actions:  # Avoid duplicates
                    actions.append(rec)

        # Add system-level coordination recommendations
        if len(self.systems_involved) > 1:
            actions.append("Establish regular cross-system coordination meetings")
            actions.append("Create shared data protocols with privacy safeguards")
            actions.append("Develop joint training programs for system stakeholders")

        # Add monitoring recommendations
        actions.append("Implement outcome tracking for system interactions")
        actions.append("Establish feedback loops for continuous improvement")

        return actions

    def generate_report(self) -> str:
        """
        Generate a comprehensive JSON report of the harm trace.

        Only generates report if safety and ethics checks have passed.
        """
        if not (self.safety_checks_passed and self.ethics_reviewed):
            return json.dumps({
                "error": "Cannot generate report: Safety and ethics checks must pass first"
            }, indent=2)

        report = {
            "harm_trace_report": {
                "metadata": {
                    "harm_description": self.harm_description,
                    "affected_parties": self.affected_parties,
                    "timestamp": self.timestamp.isoformat(),
                    "safety_checks_passed": self.safety_checks_passed,
                    "ethics_reviewed": self.ethics_reviewed
                },
                "systems_involved": [sys.to_dict() for sys in self.systems_involved],
                "interactions": [inter.to_dict() for inter in self.interactions],
                "break_points": [bp.to_dict() for bp in self.break_points],
                "safe_actions": self.generate_safe_actions()
            }
        }

        return json.dumps(report, indent=2)