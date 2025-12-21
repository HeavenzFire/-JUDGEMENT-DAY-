#!/usr/bin/env python3
"""
Guardian OS Audit System - Main Entry Point
==========================================

This system provides comprehensive auditing capabilities for Big Pharma and Military sectors,
focusing on compliance, ethics, transparency, and security monitoring.

Components:
- Data ingestion from public APIs and databases
- Guardian Network for automated monitoring
- Data processing and anomaly detection
- Web dashboard for visualization and alerts
- Database storage with integrity checks

Usage:
    python main.py --mode [ingest|audit|dashboard|test]
"""

import argparse
import sys
import pandas as pd
from datetime import datetime
import requests
import json
import time

# Import our modules
from database_setup import DatabaseManager
from guardians import ConsensusEngine, ComplianceGuardian, EthicsGuardian, TransparencyGuardian, SecurityGuardian
from data_processing import DataProcessor
from dashboard import app

class GuardianOSAudit:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.data_processor = DataProcessor()

        # Initialize guardians
        self.compliance_guardian = ComplianceGuardian()
        self.ethics_guardian = EthicsGuardian()
        self.transparency_guardian = TransparencyGuardian()
        self.security_guardian = SecurityGuardian()

        self.consensus_engine = ConsensusEngine()
        self.consensus_engine.add_guardian(self.compliance_guardian)
        self.consensus_engine.add_guardian(self.ethics_guardian)
        self.consensus_engine.add_guardian(self.transparency_guardian)
        self.consensus_engine.add_guardian(self.security_guardian)

        print("🛡️ Guardian OS Audit System initialized")

    def run_full_audit(self):
        """Run complete audit across all data sources"""
        print("\n🔍 Starting full system audit...")

        # Load data
        print("Loading data from database...")
        adverse_events = self.db_manager.load_data('adverse_events', limit=5000)
        clinical_trials = self.db_manager.load_data('clinical_trials', limit=5000)
        sec_filings = self.db_manager.load_data('sec_filings', limit=1000)
        open_payments = self.db_manager.load_data('open_payments', limit=5000)
        federal_spending = self.db_manager.load_data('federal_spending', limit=5000)

        total_records = sum([
            len(adverse_events) if adverse_events is not None else 0,
            len(clinical_trials) if clinical_trials is not None else 0,
            len(sec_filings) if sec_filings is not None else 0,
            len(open_payments) if open_payments is not None else 0,
            len(federal_spending) if federal_spending is not None else 0
        ])

        print(f"Loaded {total_records} records for analysis")

        # Process pharma data
        print("Processing pharmaceutical data...")
        pharma_results = self.data_processor.process_pharma_data(
            adverse_events_df=adverse_events,
            clinical_trials_df=clinical_trials,
            sec_filings_df=sec_filings,
            payments_df=open_payments
        )

        # Process military data
        print("Processing military data...")
        military_results = self.data_processor.process_military_data(
            spending_df=federal_spending
        )

        # Run guardian evaluations
        print("Running Guardian Network evaluation...")

        all_alerts = []

        # Pharma audit
        if adverse_events is not None and not adverse_events.empty:
            pharma_consensus = self.consensus_engine.evaluate_all(adverse_events, context='pharma')
            all_alerts.extend(pharma_consensus['alerts'])
            print(f"Pharma audit: {len(pharma_consensus['alerts'])} alerts generated")

        # Military audit
        if federal_spending is not None and not federal_spending.empty:
            military_consensus = self.consensus_engine.evaluate_all(federal_spending, context='military')
            all_alerts.extend(military_consensus['alerts'])
            print(f"Military audit: {len(military_consensus['alerts'])} alerts generated")

        # Store alerts
        if all_alerts:
            self.db_manager.insert_audit_alerts(all_alerts)
            print(f"Stored {len(all_alerts)} alerts in database")

        # Generate summary
        severity_counts = {}
        for alert in all_alerts:
            severity = alert['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        print("
📊 Audit Summary:"        print(f"Total alerts: {len(all_alerts)}")
        print(f"Critical: {severity_counts.get('critical', 0)}")
        print(f"High: {severity_counts.get('high', 0)}")
        print(f"Medium: {severity_counts.get('medium', 0)}")
        print(f"Low: {severity_counts.get('low', 0)}")

        return {
            'total_alerts': len(all_alerts),
            'severity_breakdown': severity_counts,
            'pharma_processed': bool(pharma_results),
            'military_processed': bool(military_results)
        }

    def generate_sample_data(self):
        """Generate sample data for testing"""
        print("Generating sample data for testing...")

        # Sample adverse events
        adverse_events = pd.DataFrame({
            'safetyreportid': [f'AE{i}' for i in range(100)],
            'receivedate': ['2024-01-01'] * 100,
            'serious': ['1'] * 60 + ['0'] * 40,
            'drug_name': ['Drug A'] * 40 + ['Drug B'] * 30 + ['Drug C'] * 30
        })

        # Sample clinical trials
        clinical_trials = pd.DataFrame({
            'nct_id': [f'NCT{i}' for i in range(50)],
            'brief_title': [f'Clinical Trial {i}' for i in range(50)],
            'overall_status': ['Completed'] * 30 + ['Recruiting'] * 20,
            'enrollment_count': [100 + i*10 for i in range(50)],
            'sponsor': ['Pfizer'] * 15 + ['Merck'] * 15 + ['Other'] * 20
        })

        # Sample federal spending
        federal_spending = pd.DataFrame({
            'award_id': [f'AWARD{i}' for i in range(50)],
            'recipient_name': ['Company A'] * 20 + ['Company B'] * 15 + ['Company C'] * 15,
            'awarding_agency': ['Department of Defense'] * 30 + ['Department of Health'] * 20,
            'award_amount': [1000000 + i*50000 for i in range(50)],
            'description': ['Defense contract'] * 30 + ['Medical research'] * 20
        })

        # Insert sample data
        self.db_manager.insert_adverse_events(adverse_events)
        self.db_manager.insert_clinical_trials(clinical_trials)
        self.db_manager.insert_federal_spending(federal_spending)

        print("Sample data generated and inserted")

    def run_dashboard(self):
        """Start the web dashboard"""
        print("Starting Guardian OS Dashboard...")
        print("Access at: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)

    def test_system(self):
        """Run system tests"""
        print("Running system tests...")

        # Test database connection
        try:
            stats = self.db_manager.get_table_stats()
            print(f"✅ Database connection: OK ({sum(stats.values())} total records)")
        except Exception as e:
            print(f"❌ Database connection: FAILED ({e})")
            return False

        # Test data processing
        try:
            sample_data = pd.DataFrame({'test': [1, 2, 3]})
            result = self.data_processor.process_pharma_data(adverse_events_df=sample_data)
            print("✅ Data processing: OK")
        except Exception as e:
            print(f"❌ Data processing: FAILED ({e})")
            return False

        # Test guardians
        try:
            consensus = self.consensus_engine.evaluate_all(sample_data, context='pharma')
            print(f"✅ Guardian Network: OK ({len(consensus['alerts'])} alerts generated)")
        except Exception as e:
            print(f"❌ Guardian Network: FAILED ({e})")
            return False

        print("🎉 All system tests passed!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Guardian OS Audit System')
    parser.add_argument('--mode', choices=['audit', 'dashboard', 'test', 'sample-data'],
                       default='dashboard', help='Operation mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Initialize system
    guardian_os = GuardianOSAudit()

    if args.mode == 'audit':
        # Run full audit
        results = guardian_os.run_full_audit()
        print(f"\nAudit completed: {results['total_alerts']} alerts generated")

    elif args.mode == 'dashboard':
        # Start dashboard
        guardian_os.run_dashboard()

    elif args.mode == 'test':
        # Run tests
        success = guardian_os.test_system()
        sys.exit(0 if success else 1)

    elif args.mode == 'sample-data':
        # Generate sample data
        guardian_os.generate_sample_data()
        print("Sample data generation completed")

if __name__ == "__main__":
    main()