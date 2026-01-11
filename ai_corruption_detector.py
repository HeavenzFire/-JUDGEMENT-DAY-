"""
AI-Powered Corruption Detection System

Uses machine learning to detect fraud patterns in public contracts,
government spending, and procurement processes.

This addresses the critical challenge of systemic corruption that enables
trafficking and other organized crimes.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
import json


class ContractAnalyzer:
    """Analyzes individual contracts for corruption indicators"""

    def __init__(self):
        self.corruption_indicators = {
            'price_anomalies': ['unusually_high_bid', 'unusually_low_bid', 'round_number_pricing'],
            'timing_issues': ['rush_procurement', 'weekend_award', 'holiday_award'],
            'relationship_red_flags': ['family_connections', 'political_donations', 'previous_convictions'],
            'competition_concerns': ['single_bidder', 'bidder_elimination', 'late_changes'],
            'documentation_issues': ['missing_documents', 'incomplete_specs', 'vague_requirements']
        }

    def analyze_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single contract for corruption indicators"""
        risk_score = 0.0
        flags = []
        recommendations = []

        # Price anomaly detection
        if self._detect_price_anomaly(contract_data):
            risk_score += 0.3
            flags.append('price_anomaly')
            recommendations.append('Conduct independent price comparison')

        # Timing analysis
        if self._detect_timing_issues(contract_data):
            risk_score += 0.2
            flags.append('timing_issue')
            recommendations.append('Review procurement timeline for irregularities')

        # Relationship analysis
        if self._detect_relationship_red_flags(contract_data):
            risk_score += 0.4
            flags.append('relationship_red_flag')
            recommendations.append('Investigate bidder-awardee relationships')

        # Competition analysis
        if self._detect_competition_concerns(contract_data):
            risk_score += 0.25
            flags.append('competition_concern')
            recommendations.append('Verify competitive bidding process')

        # Documentation check
        if self._detect_documentation_issues(contract_data):
            risk_score += 0.15
            flags.append('documentation_issue')
            recommendations.append('Complete missing documentation')

        # Risk level classification
        if risk_score >= 0.7:
            risk_level = 'HIGH'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'contract_id': contract_data.get('contract_id', 'unknown'),
            'risk_score': min(risk_score, 1.0),
            'risk_level': risk_level,
            'flags': flags,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def _detect_price_anomaly(self, contract: Dict[str, Any]) -> bool:
        """Detect unusual pricing patterns"""
        bid_amount = contract.get('bid_amount', 0)
        estimated_value = contract.get('estimated_value', 0)

        if estimated_value == 0:
            return False

        ratio = bid_amount / estimated_value

        # Check for extreme deviations
        if ratio > 2.0 or ratio < 0.5:
            return True

        # Check for round numbers (potential bid rigging)
        bid_str = str(int(bid_amount))
        if len(bid_str) > 3 and bid_str.endswith('00000'):
            return True

        return False

    def _detect_timing_issues(self, contract: Dict[str, Any]) -> bool:
        """Detect suspicious timing in procurement"""
        award_date = contract.get('award_date')
        if not award_date:
            return False

        try:
            award_dt = datetime.fromisoformat(award_date.replace('Z', '+00:00'))

            # Check for weekend awards
            if award_dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return True

            # Check for holiday periods (simplified)
            month = award_dt.month
            day = award_dt.day
            if (month == 12 and day >= 20) or (month == 1 and day <= 5):  # Christmas/New Year
                return True

        except (ValueError, AttributeError):
            pass

        return False

    def _detect_relationship_red_flags(self, contract: Dict[str, Any]) -> bool:
        """Detect concerning relationships between bidders and awardees"""
        # This would integrate with external databases in production
        # For demo, check for obvious flags in contract data

        bidder_name = contract.get('bidder_name', '').lower()
        awardee_name = contract.get('awardee_name', '').lower()

        # Check for family relationships (simplified)
        family_indicators = ['son', 'daughter', 'brother', 'sister', 'father', 'mother', 'wife', 'husband']
        for indicator in family_indicators:
            if indicator in bidder_name and indicator in awardee_name:
                return True

        # Check for political connections (simplified)
        political_terms = ['party', 'campaign', 'election', 'politician']
        contract_desc = contract.get('description', '').lower()
        for term in political_terms:
            if term in contract_desc:
                return True

        return False

    def _detect_competition_concerns(self, contract: Dict[str, Any]) -> bool:
        """Detect lack of proper competition"""
        num_bidders = contract.get('num_bidders', 1)

        if num_bidders == 1:
            return True  # Single bidder is always concerning

        if num_bidders < 3:
            return True  # Very limited competition

        return False

    def _detect_documentation_issues(self, contract: Dict[str, Any]) -> bool:
        """Check for incomplete or missing documentation"""
        required_fields = ['description', 'bid_amount', 'award_date', 'bidder_name']
        missing_fields = []

        for field in required_fields:
            if not contract.get(field):
                missing_fields.append(field)

        return len(missing_fields) > 0


class AICorruptionDetector:
    """
    Machine learning system for detecting corruption patterns across
    large datasets of contracts and procurement records.
    """

    def __init__(self):
        self.contract_analyzer = ContractAnalyzer()
        self.rf_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False

    def preprocess_data(self, contracts_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess contract data for ML training"""
        # Select features for ML
        feature_columns = [
            'bid_amount', 'estimated_value', 'num_bidders',
            'contract_duration_days', 'supplier_experience_years'
        ]

        # Handle missing values
        df = contracts_df.copy()
        for col in feature_columns:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median() if df[col].dtype in ['int64', 'float64'] else 0)

        # Create target variable (corruption label)
        # In production, this would come from verified corruption cases
        df['is_corrupt'] = self._generate_synthetic_labels(df)

        # Encode categorical variables
        categorical_columns = ['contract_type', 'supplier_location', 'procurement_method']
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[col] = self.label_encoders[col].transform(df[col].astype(str))

        # Prepare features
        X = df[feature_columns].values
        y = df['is_corrupt'].values

        # Scale features
        X = self.scaler.fit_transform(X)

        return X, y

    def _generate_synthetic_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Generate synthetic corruption labels for training (demo purposes)"""
        # In production, this would use verified corruption cases
        np.random.seed(42)
        labels = np.zeros(len(df), dtype=int)

        # Mark some contracts as corrupt based on suspicious patterns
        suspicious_mask = (
            (df['num_bidders'] == 1) |
            (df['bid_amount'] > df['estimated_value'] * 1.5) |
            (df['contract_duration_days'] > 365*2)
        )

        labels[suspicious_mask] = 1
        return labels

    def train_models(self, contracts_df: pd.DataFrame) -> Dict[str, Any]:
        """Train the ML models on contract data"""
        print("Training AI corruption detection models...")

        X, y = self.preprocess_data(contracts_df)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train Random Forest classifier
        self.rf_classifier.fit(X_train, y_train)
        rf_predictions = self.rf_classifier.predict(X_test)
        rf_proba = self.rf_classifier.predict_proba(X_test)[:, 1]

        # Train Isolation Forest for anomaly detection
        self.isolation_forest.fit(X_train)

        # Calculate metrics
        training_results = {
            'random_forest': {
                'accuracy': self.rf_classifier.score(X_test, y_test),
                'auc_score': roc_auc_score(y_test, rf_proba),
                'classification_report': classification_report(y_test, rf_predictions, output_dict=True)
            },
            'isolation_forest': {
                'contamination_estimate': self.isolation_forest.contamination
            }
        }

        self.is_trained = True
        print("✅ Models trained successfully!")
        return training_results

    def detect_corruption(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect corruption in a single contract using trained models"""
        if not self.is_trained:
            return self.contract_analyzer.analyze_contract(contract_data)

        # Rule-based analysis
        rule_based = self.contract_analyzer.analyze_contract(contract_data)

        # ML-based analysis
        ml_features = self._extract_ml_features(contract_data)
        if ml_features is not None:
            ml_features_scaled = self.scaler.transform([ml_features])

            # Random Forest prediction
            rf_proba = self.rf_classifier.predict_proba(ml_features_scaled)[0][1]
            rf_prediction = self.rf_classifier.predict(ml_features_scaled)[0]

            # Isolation Forest anomaly score
            anomaly_score = self.isolation_forest.decision_function(ml_features_scaled)[0]
            is_anomaly = self.isolation_forest.predict(ml_features_scaled)[0] == -1

            ml_analysis = {
                'rf_corruption_probability': float(rf_proba),
                'rf_prediction': 'corrupt' if rf_prediction == 1 else 'clean',
                'anomaly_score': float(anomaly_score),
                'is_anomaly': bool(is_anomaly)
            }
        else:
            ml_analysis = {
                'error': 'Insufficient data for ML analysis'
            }

        # Combine analyses
        combined_risk = rule_based['risk_score']
        if 'rf_corruption_probability' in ml_analysis:
            combined_risk = (combined_risk + ml_analysis['rf_corruption_probability']) / 2

        if ml_analysis.get('is_anomaly', False):
            combined_risk += 0.2

        # Adjust risk level
        if combined_risk >= 0.7:
            combined_level = 'HIGH'
        elif combined_risk >= 0.4:
            combined_level = 'MEDIUM'
        else:
            combined_level = 'LOW'

        return {
            'contract_id': contract_data.get('contract_id', 'unknown'),
            'rule_based_analysis': rule_based,
            'ml_analysis': ml_analysis,
            'combined_risk_score': min(combined_risk, 1.0),
            'combined_risk_level': combined_level,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def _extract_ml_features(self, contract: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract ML features from contract data"""
        try:
            features = [
                contract.get('bid_amount', 0),
                contract.get('estimated_value', 0),
                contract.get('num_bidders', 1),
                contract.get('contract_duration_days', 30),
                contract.get('supplier_experience_years', 0)
            ]
            return np.array(features)
        except (TypeError, ValueError):
            return None

    def audit_procurement_system(self, contracts_df: pd.DataFrame) -> Dict[str, Any]:
        """Audit an entire procurement system for corruption patterns"""
        print("Auditing procurement system...")

        audit_results = {
            'total_contracts': len(contracts_df),
            'high_risk_contracts': 0,
            'total_contract_value': 0,
            'potentially_corrupt_value': 0,
            'risk_distribution': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'common_flags': {},
            'recommendations': []
        }

        for _, contract in contracts_df.iterrows():
            contract_dict = contract.to_dict()
            analysis = self.detect_corruption(contract_dict)

            audit_results['total_contract_value'] += contract_dict.get('bid_amount', 0)

            risk_level = analysis['combined_risk_level']
            audit_results['risk_distribution'][risk_level] += 1

            if risk_level == 'HIGH':
                audit_results['high_risk_contracts'] += 1
                audit_results['potentially_corrupt_value'] += contract_dict.get('bid_amount', 0)

            # Track common flags
            if 'rule_based_analysis' in analysis:
                for flag in analysis['rule_based_analysis']['flags']:
                    audit_results['common_flags'][flag] = audit_results['common_flags'].get(flag, 0) + 1

        # Generate recommendations
        if audit_results['high_risk_contracts'] > len(contracts_df) * 0.1:
            audit_results['recommendations'].append(
                "URGENT: High proportion of high-risk contracts detected. Recommend comprehensive audit."
            )

        corrupt_value_pct = audit_results['potentially_corrupt_value'] / max(1, audit_results['total_contract_value'])
        if corrupt_value_pct > 0.2:
            audit_results['recommendations'].append(
                f"HIGH VALUE AT RISK: {corrupt_value_pct:.1%} of contract value shows corruption indicators."
            )

        return audit_results


def generate_synthetic_contracts(num_contracts: int = 1000) -> pd.DataFrame:
    """Generate synthetic contract data for testing"""
    np.random.seed(42)

    contracts = []

    contract_types = ['construction', 'IT_services', 'consulting', 'supplies', 'maintenance']
    locations = ['urban', 'rural', 'suburban']
    procurement_methods = ['open_bid', 'restricted', 'direct_award']

    for i in range(num_contracts):
        contract_value = np.random.lognormal(10, 1.5)  # Mean ~$22,000

        # Introduce some corruption patterns
        is_corrupt = np.random.random() < 0.15  # 15% corruption rate

        if is_corrupt:
            # Corrupt contracts have suspicious patterns
            num_bidders = np.random.choice([1, 2])  # Limited competition
            if np.random.random() < 0.5:
                contract_value *= np.random.uniform(1.3, 2.0)  # Overpriced
        else:
            num_bidders = np.random.randint(3, 8)  # Normal competition

        contract = {
            'contract_id': f"CONTRACT_{i:04d}",
            'contract_type': np.random.choice(contract_types),
            'bid_amount': contract_value,
            'estimated_value': contract_value * np.random.uniform(0.8, 1.2),
            'num_bidders': num_bidders,
            'contract_duration_days': np.random.randint(30, 365*3),
            'supplier_experience_years': np.random.randint(0, 20),
            'supplier_location': np.random.choice(locations),
            'procurement_method': np.random.choice(procurement_methods),
            'award_date': (datetime.now() - timedelta(days=np.random.randint(1, 365))).isoformat(),
            'bidder_name': f"Supplier_{np.random.randint(1, 100)}",
            'description': f"Procurement of {np.random.choice(contract_types)} services"
        }

        contracts.append(contract)

    return pd.DataFrame(contracts)


def demonstrate_ai_corruption_detection():
    """Demonstrate the AI corruption detection system"""
    print("🧠 AI-POWERED CORRUPTION DETECTION SYSTEM")
    print("=" * 60)

    detector = AICorruptionDetector()

    # Generate synthetic contract data
    print("Generating synthetic contract dataset...")
    contracts_df = generate_synthetic_contracts(1000)
    print(f"Created {len(contracts_df)} synthetic contracts")

    # Train the models
    training_results = detector.train_models(contracts_df)

    print("\n📊 Training Results:")
    rf_results = training_results['random_forest']
    print(f"Random Forest Accuracy: {rf_results['accuracy']:.3f}")
    print(f"AUC Score: {rf_results['auc_score']:.3f}")

    # Test on individual contracts
    print("\n🔍 Testing Individual Contract Analysis:")
    test_contracts = contracts_df.sample(5, random_state=42)

    for _, contract in test_contracts.iterrows():
        analysis = detector.detect_corruption(contract.to_dict())
        print(f"Contract {contract['contract_id']}: {analysis['combined_risk_level']} risk "
              f"(score: {analysis['combined_risk_score']:.2f})")

    # Audit entire system
    print("\n📈 System-wide Audit:")
    audit_results = detector.audit_procurement_system(contracts_df)

    print(f"Total Contracts: {audit_results['total_contracts']}")
    print(f"High Risk Contracts: {audit_results['high_risk_contracts']}")
    print(f"Risk Distribution: {audit_results['risk_distribution']}")
    print(f"Potentially Corrupt Value: ${audit_results['potentially_corrupt_value']:,.0f}")
    print(f"Common Flags: {audit_results['common_flags']}")

    if audit_results['recommendations']:
        print("\n⚠️ Recommendations:")
        for rec in audit_results['recommendations']:
            print(f"  • {rec}")

    print("\n✅ AI corruption detection system operational!")
    print("This system can detect fraud patterns in government procurement and contracts.")


if __name__ == "__main__":
    demonstrate_ai_corruption_detection()