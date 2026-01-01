#!/usr/bin/env python3
"""
Test script for Harm System Tracer

Demonstrates tracing harm across example systems (legal and healthcare interactions).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from harm_system_tracer import System, HarmTrace, SystemInteraction, BreakPoint
from datetime import datetime


def create_example_systems():
    """Create example systems for testing."""
    legal_system = System(
        name="Family Court System",
        category="legal",
        description="Handles child custody, protection, and welfare cases",
        stakeholders=["judges", "attorneys", "social workers", "families"],
        protocols=["due process", "best interest standard"],
        risks=["case backlogs", "inconsistent rulings", "lack of resources"]
    )

    healthcare_system = System(
        name="Pediatric Healthcare Network",
        category="healthcare",
        description="Provides medical care and mental health services for children",
        stakeholders=["doctors", "nurses", "therapists", "families"],
        protocols=["HIPAA compliance", "mandatory reporting"],
        risks=["long wait times", "insurance barriers", "staff shortages"]
    )

    child_welfare_system = System(
        name="Child Protective Services",
        category="child_welfare",
        description="Investigates reports of child abuse and neglect",
        stakeholders=["case workers", "investigators", "foster care providers"],
        protocols=["immediate safety assessment", "family preservation"],
        risks=["high caseloads", "false positives", "resource limitations"]
    )

    return legal_system, healthcare_system, child_welfare_system


def create_example_trace():
    """Create an example harm trace scenario."""
    # Create systems
    legal, healthcare, child_welfare = create_example_systems()

    # Create harm trace
    trace = HarmTrace(
        harm_description="Delayed intervention in child abuse case due to poor inter-system communication",
        affected_parties=["child victim", "family members", "community"]
    )

    # Add systems to trace
    trace.add_system(legal)
    trace.add_system(healthcare)
    trace.add_system(child_welfare)

    # Create system interactions
    referral_interaction = SystemInteraction(
        systems=["Pediatric Healthcare Network", "Child Protective Services"],
        interaction_type="referral",
        description="Healthcare providers reporting suspected abuse to CPS",
        frequency="occasional",
        success_rate=0.7
    )

    court_interaction = SystemInteraction(
        systems=["Child Protective Services", "Family Court System"],
        interaction_type="oversight",
        description="CPS presenting cases to family court for judicial review",
        frequency="frequent",
        success_rate=0.8
    )

    # Add break points
    delayed_reporting_bp = BreakPoint(
        description="Healthcare providers delayed mandatory reporting due to unclear protocols",
        systems_involved=["Pediatric Healthcare Network", "Child Protective Services"],
        severity="high"
    )
    delayed_reporting_bp.add_evidence("Provider waited 3 days to report suspected abuse")
    delayed_reporting_bp.add_evidence("Unclear guidelines on when to report vs. when to monitor")
    delayed_reporting_bp.add_recommendation("Standardize mandatory reporting training across healthcare providers")
    delayed_reporting_bp.add_recommendation("Implement automated reporting checklists in EHR systems")

    court_backlog_bp = BreakPoint(
        description="Family court backlog caused 6-week delay in emergency custody hearing",
        systems_involved=["Child Protective Services", "Family Court System"],
        severity="critical"
    )
    court_backlog_bp.add_evidence("Court docket shows average 45-day wait for emergency hearings")
    court_backlog_bp.add_evidence("Child remained in unsafe home environment during delay")
    court_backlog_bp.add_recommendation("Increase judicial resources for child welfare cases")
    court_backlog_bp.add_recommendation("Implement fast-track procedures for urgent child safety matters")

    # Add break points to interactions
    referral_interaction.add_break_point(delayed_reporting_bp)
    court_interaction.add_break_point(court_backlog_bp)

    # Add interactions to trace
    trace.add_interaction(referral_interaction)
    trace.add_interaction(court_interaction)

    # Add break points directly to trace
    trace.add_break_point(delayed_reporting_bp)
    trace.add_break_point(court_backlog_bp)

    return trace


def run_tests():
    """Run comprehensive tests of the harm tracing framework."""
    print("=== Harm System Tracer Tests ===\n")

    # Test 1: System creation and methods
    print("1. Testing System class...")
    legal_sys = System("Test Legal", "legal", "Test description")
    legal_sys.add_stakeholder("judge")
    legal_sys.add_risk("backlog")
    assert len(legal_sys.stakeholders) == 1
    assert len(legal_sys.risks) == 1
    print("✓ System class tests passed")

    # Test 2: BreakPoint creation and methods
    print("\n2. Testing BreakPoint class...")
    bp = BreakPoint("Test break point", ["system1", "system2"], "medium")
    bp.add_evidence("evidence1")
    bp.add_recommendation("recommendation1")
    assert len(bp.evidence) == 1
    assert len(bp.recommendations) == 1
    print("✓ BreakPoint class tests passed")

    # Test 3: SystemInteraction creation
    print("\n3. Testing SystemInteraction class...")
    interaction = SystemInteraction(
        ["sys1", "sys2"], "data_sharing", "Test interaction", "frequent", 0.85
    )
    interaction.add_break_point(bp)
    assert len(interaction.break_points) == 1
    print("✓ SystemInteraction class tests passed")

    # Test 4: HarmTrace creation and safety checks
    print("\n4. Testing HarmTrace class...")
    trace = create_example_trace()

    # Test safety check
    safety_passed = trace.perform_safety_check()
    print(f"Safety check passed: {safety_passed}")

    # Test ethics review
    ethics_passed = trace.perform_ethics_review()
    print(f"Ethics review passed: {ethics_passed}")

    if safety_passed and ethics_passed:
        # Generate report
        report = trace.generate_report()
        print("✓ Report generated successfully")

        # Generate safe actions
        actions = trace.generate_safe_actions()
        print(f"✓ Generated {len(actions)} safe action recommendations")

        # Print summary
        print("\n=== Trace Summary ===")
        print(f"Harm: {trace.harm_description}")
        print(f"Systems involved: {len(trace.systems_involved)}")
        print(f"Interactions: {len(trace.interactions)}")
        print(f"Break points: {len(trace.break_points)}")

        print("\n=== Safe Actions ===")
        for i, action in enumerate(actions, 1):
            print(f"{i}. {action}")

    else:
        print("✗ Safety or ethics checks failed")

    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    run_tests()