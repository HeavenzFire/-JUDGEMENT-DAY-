import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class Guardian:
    def __init__(self, name):
        self.name = name
        self.alerts = []

    def evaluate(self, data, context=None):
        """Evaluate data for compliance issues"""
        raise NotImplementedError

    def add_alert(self, alert_type, severity, description, data_point=None):
        """Add an alert to the guardian's log"""
        alert = {
            'timestamp': datetime.now(),
            'guardian': self.name,
            'type': alert_type,
            'severity': severity,  # 'low', 'medium', 'high', 'critical'
            'description': description,
            'data_point': data_point
        }
        self.alerts.append(alert)
        return alert

    def get_alerts(self, severity_filter=None):
        """Get alerts, optionally filtered by severity"""
        if severity_filter:
            return [a for a in self.alerts if a['severity'] == severity_filter]
        return self.alerts

class ComplianceGuardian(Guardian):
    def __init__(self):
        super().__init__("Compliance Guardian")
        self.regulatory_frameworks = {
            'FDA': {
                'max_adverse_events_threshold': 1000,
                'required_reporting_period': 15  # days
            },
            'EMA': {
                'max_adverse_events_threshold': 500,
                'required_reporting_period': 15
            }
        }

    def evaluate(self, data, context='pharma'):
        """Evaluate compliance with regulatory requirements"""
        alerts = []

        if context == 'pharma':
            alerts.extend(self._evaluate_pharma_compliance(data))
        elif context == 'military':
            alerts.extend(self._evaluate_military_compliance(data))

        return alerts

    def _evaluate_pharma_compliance(self, data):
        """Evaluate pharmaceutical compliance"""
        alerts = []

        if 'adverse_events' in data.columns:
            # Check for drugs with excessive adverse events
            adverse_summary = data.groupby('drug_name').agg({
                'safetyreportid': 'count',
                'serious': lambda x: (x == '1').sum()
            }).reset_index()

            for _, row in adverse_summary.iterrows():
                if row['safetyreportid'] > self.regulatory_frameworks['FDA']['max_adverse_events_threshold']:
                    alerts.append(self.add_alert(
                        'excessive_adverse_events',
                        'high',
                        f"Drug '{row['drug_name']}' has {row['safetyreportid']} adverse events, exceeding FDA threshold",
                        {'drug': row['drug_name'], 'count': row['safetyreportid']}
                    ))

                serious_rate = row['serious'] / row['safetyreportid'] if row['safetyreportid'] > 0 else 0
                if serious_rate > 0.5:  # More than 50% serious events
                    alerts.append(self.add_alert(
                        'high_serious_event_rate',
                        'critical',
                        f"Drug '{row['drug_name']}' has {serious_rate:.1%} serious adverse events",
                        {'drug': row['drug_name'], 'serious_rate': serious_rate}
                    ))

        if 'approval_date' in data.columns:
            # Check for overdue safety reports
            data['approval_date'] = pd.to_datetime(data['approval_date'], errors='coerce')
            current_date = datetime.now()

            for _, row in data.iterrows():
                if pd.notna(row['approval_date']):
                    days_since_approval = (current_date - row['approval_date']).days
                    if days_since_approval > 365 and pd.isna(row.get('last_safety_report')):
                        alerts.append(self.add_alert(
                            'missing_safety_report',
                            'medium',
                            f"Drug '{row.get('product_name', 'Unknown')}' missing annual safety report ({days_since_approval} days since approval)",
                            {'drug': row.get('product_name'), 'days_overdue': days_since_approval}
                        ))

        return alerts

    def _evaluate_military_compliance(self, data):
        """Evaluate military procurement compliance"""
        alerts = []

        if 'award_amount' in data.columns:
            # Check for unusually large contracts
            mean_amount = data['award_amount'].mean()
            std_amount = data['award_amount'].std()

            for _, row in data.iterrows():
                if row['award_amount'] > mean_amount + 3 * std_amount:
                    alerts.append(self.add_alert(
                        'unusually_large_contract',
                        'high',
                        f"Contract {row['award_id']} amount (${row['award_amount']:,.0f}) is unusually large",
                        {'contract_id': row['award_id'], 'amount': row['award_amount']}
                    ))

        if 'description' in data.columns:
            # Check for vague contract descriptions
            for _, row in data.iterrows():
                desc = str(row['description']).lower()
                if len(desc.split()) < 5 or 'tbd' in desc or 'to be determined' in desc:
                    alerts.append(self.add_alert(
                        'vague_contract_description',
                        'medium',
                        f"Contract {row['award_id']} has vague description: '{row['description']}'",
                        {'contract_id': row['award_id'], 'description': row['description']}
                    ))

        return alerts

class EthicsGuardian(Guardian):
    def __init__(self):
        super().__init__("Ethics Guardian")
        self.ethical_concerns = {
            'conflicts_of_interest': ['consulting', 'board member', 'investor'],
            'animal_testing': ['animal', 'vivisection', 'toxicity'],
            'human_rights': ['detention', 'interrogation', 'surveillance']
        }

    def evaluate(self, data, context='pharma'):
        """Evaluate ethical considerations"""
        alerts = []

        if context == 'pharma':
            alerts.extend(self._evaluate_pharma_ethics(data))
        elif context == 'military':
            alerts.extend(self._evaluate_military_ethics(data))

        return alerts

    def _evaluate_pharma_ethics(self, data):
        """Evaluate pharmaceutical ethics"""
        alerts = []

        if 'brief_title' in data.columns:
            # Check for potentially unethical trial designs
            for _, row in data.iterrows():
                title = str(row['brief_title']).lower()

                # Check for placebo vs active comparator issues
                if 'placebo' in title and 'superiority' in title:
                    if row.get('enrollment_count', 0) < 50:
                        alerts.append(self.add_alert(
                            'potentially_unethical_trial_design',
                            'medium',
                            f"Trial '{row['brief_title']}' uses placebo in small study (n={row.get('enrollment_count', 0)})",
                            {'trial_id': row['nct_id'], 'enrollment': row.get('enrollment_count')}
                        ))

        if 'sponsor' in data.columns:
            # Check for sponsor influence concerns
            pharma_companies = ['pfizer', 'merck', 'johnson', 'bayer', 'novartis', 'roche']

            for _, row in data.iterrows():
                sponsor = str(row['sponsor']).lower()
                if any(company in sponsor for company in pharma_companies):
                    # Check if trial is industry-sponsored
                    alerts.append(self.add_alert(
                        'industry_sponsored_trial',
                        'low',
                        f"Trial '{row['brief_title']}' sponsored by {row['sponsor']} - monitor for bias",
                        {'trial_id': row['nct_id'], 'sponsor': row['sponsor']}
                    ))

        return alerts

    def _evaluate_military_ethics(self, data):
        """Evaluate military ethics"""
        alerts = []

        if 'description' in data.columns:
            # Check for ethically concerning contract purposes
            for _, row in data.iterrows():
                desc = str(row['description']).lower()

                if any(term in desc for term in self.ethical_concerns['human_rights']):
                    alerts.append(self.add_alert(
                        'human_rights_concern',
                        'high',
                        f"Contract {row['award_id']} may involve human rights issues: '{row['description']}'",
                        {'contract_id': row['award_id'], 'description': row['description']}
                    ))

        return alerts

class TransparencyGuardian(Guardian):
    def __init__(self):
        super().__init__("Transparency Guardian")

    def evaluate(self, data, context='pharma'):
        """Evaluate transparency and disclosure requirements"""
        alerts = []

        if context == 'pharma':
            alerts.extend(self._evaluate_pharma_transparency(data))
        elif context == 'military':
            alerts.extend(self._evaluate_military_transparency(data))

        return alerts

    def _evaluate_pharma_transparency(self, data):
        """Evaluate pharmaceutical transparency"""
        alerts = []

        if 'overall_status' in data.columns:
            # Check for completed trials without results
            completed_trials = data[data['overall_status'] == 'Completed']
            current_date = datetime.now()

            for _, row in completed_trials.iterrows():
                if row.get('completion_date'):
                    completion_date = pd.to_datetime(row['completion_date'], errors='coerce')
                    if pd.notna(completion_date):
                        days_since_completion = (current_date - completion_date).days
                        if days_since_completion > 365:  # No results posted within a year
                            alerts.append(self.add_alert(
                                'missing_trial_results',
                                'medium',
                                f"Trial '{row['brief_title']}' completed {days_since_completion} days ago without results posted",
                                {'trial_id': row['nct_id'], 'days_overdue': days_since_completion}
                            ))

        return alerts

    def _evaluate_military_transparency(self, data):
        """Evaluate military transparency"""
        alerts = []

        if 'recipient_name' in data.columns:
            # Check for contracts awarded to anonymous or shell companies
            suspicious_patterns = ['llc', 'ltd', 'inc', 'corp']

            for _, row in data.iterrows():
                recipient = str(row['recipient_name']).lower()
                if len(recipient.split()) <= 2 and any(pattern in recipient for pattern in suspicious_patterns):
                    alerts.append(self.add_alert(
                        'potentially_shell_company',
                        'medium',
                        f"Contract awarded to potentially shell company: '{row['recipient_name']}'",
                        {'contract_id': row['award_id'], 'recipient': row['recipient_name']}
                    ))

        return alerts

class SecurityGuardian(Guardian):
    def __init__(self):
        super().__init__("Security Guardian")

    def evaluate(self, data, context='pharma'):
        """Evaluate data security and privacy concerns"""
        alerts = []

        # Check for sensitive data exposure
        sensitive_patterns = {
            'pii': [r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            'financial': [r'\$\d+(?:\.\d{2})?', r'\b\d+(?:\.\d{2})?\s*(?:million|billion)\b'],
            'health': [r'\b(?:HIV|AIDS|diabetes|cancer)\b']
        }

        for column in data.columns:
            if data[column].dtype == 'object':
                for pattern_name, patterns in sensitive_patterns.items():
                    for pattern in patterns:
                        matches = data[column].astype(str).str.contains(pattern, regex=True, na=False)
                        if matches.any():
                            count = matches.sum()
                            alerts.append(self.add_alert(
                                'sensitive_data_exposure',
                                'critical',
                                f"Column '{column}' contains {count} instances of {pattern_name} data",
                                {'column': column, 'pattern': pattern_name, 'count': count}
                            ))

        # Check for data quality issues
        for column in data.columns:
            null_count = data[column].isnull().sum()
            if null_count > len(data) * 0.5:  # More than 50% null
                alerts.append(self.add_alert(
                    'poor_data_quality',
                    'low',
                    f"Column '{column}' has {null_count}/{len(data)} null values ({null_count/len(data):.1%})",
                    {'column': column, 'null_count': null_count, 'total': len(data)}
                ))

        return alerts

class ConsensusEngine:
    def __init__(self):
        self.guardians = []

    def add_guardian(self, guardian):
        self.guardians.append(guardian)

    def evaluate_all(self, data, context='pharma'):
        """Run all guardians and collect consensus"""
        all_alerts = []

        for guardian in self.guardians:
            alerts = guardian.evaluate(data, context)
            all_alerts.extend(alerts)

        # Group alerts by severity
        severity_counts = {}
        for alert in all_alerts:
            severity = alert['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        consensus = {
            'total_alerts': len(all_alerts),
            'severity_breakdown': severity_counts,
            'alerts': all_alerts,
            'critical_issues': [a for a in all_alerts if a['severity'] == 'critical'],
            'high_priority': [a for a in all_alerts if a['severity'] in ['high', 'critical']]
        }

        return consensus

# Example usage
if __name__ == "__main__":
    # Create guardians
    compliance = ComplianceGuardian()
    ethics = EthicsGuardian()
    transparency = TransparencyGuardian()
    security = SecurityGuardian()

    # Create consensus engine
    engine = ConsensusEngine()
    engine.add_guardian(compliance)
    engine.add_guardian(ethics)
    engine.add_guardian(transparency)
    engine.add_guardian(security)

    # Load sample data (would normally come from data_ingestion.py)
    sample_data = pd.DataFrame({
        'drug_name': ['Drug A', 'Drug B', 'Drug A'],
        'safetyreportid': [1, 2, 3],
        'serious': ['1', '0', '1']
    })

    # Run evaluation
    results = engine.evaluate_all(sample_data, context='pharma')

    print(f"Total alerts: {results['total_alerts']}")
    print(f"Severity breakdown: {results['severity_breakdown']}")
    print(f"Critical issues: {len(results['critical_issues'])}")
    print(f"High priority items: {len(results['high_priority'])}")