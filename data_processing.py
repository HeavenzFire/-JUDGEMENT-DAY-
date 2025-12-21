import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pyod.models import IForest, HBOS, KNN
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    def __init__(self):
        self.models = {
            'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
            'pyod_iforest': IForest(contamination=0.1, random_state=42),
            'hbos': HBOS(contamination=0.1),
            'knn': KNN(contamination=0.1)
        }
        self.scaler = StandardScaler()

    def detect_anomalies(self, data, features, method='isolation_forest'):
        """Detect anomalies in numerical data"""
        if method not in self.models:
            raise ValueError(f"Unknown method: {method}")

        # Prepare data
        X = data[features].dropna()
        if len(X) == 0:
            return pd.Series([], dtype=int)

        # Scale data
        X_scaled = self.scaler.fit_transform(X)

        # Fit model
        model = self.models[method]
        model.fit(X_scaled)

        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = model.predict(X_scaled)

        # Create result series aligned with original data
        result = pd.Series(index=X.index, dtype=int)
        result.loc[X.index] = predictions

        return result

    def detect_statistical_anomalies(self, data, column, method='zscore', threshold=3):
        """Detect anomalies using statistical methods"""
        values = data[column].dropna()

        if method == 'zscore':
            z_scores = np.abs((values - values.mean()) / values.std())
            return z_scores > threshold
        elif method == 'iqr':
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (values < lower_bound) | (values > upper_bound)
        else:
            raise ValueError(f"Unknown statistical method: {method}")

class DataProcessor:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()

    def process_pharma_data(self, adverse_events_df=None, clinical_trials_df=None,
                          sec_filings_df=None, payments_df=None):
        """Process pharmaceutical data for analysis"""
        results = {}

        # Process adverse events
        if adverse_events_df is not None and not adverse_events_df.empty:
            results['adverse_events_analysis'] = self._analyze_adverse_events(adverse_events_df)

        # Process clinical trials
        if clinical_trials_df is not None and not clinical_trials_df.empty:
            results['clinical_trials_analysis'] = self._analyze_clinical_trials(clinical_trials_df)

        # Process SEC filings
        if sec_filings_df is not None and not sec_filings_df.empty:
            results['financial_analysis'] = self._analyze_financial_data(sec_filings_df)

        # Process payments
        if payments_df is not None and not payments_df.empty:
            results['payments_analysis'] = self._analyze_payments(payments_df)

        # Cross-reference analysis
        if len(results) > 1:
            results['cross_reference_analysis'] = self._cross_reference_analysis(results)

        return results

    def process_military_data(self, spending_df=None, contracts_df=None):
        """Process military data for analysis"""
        results = {}

        # Process spending data
        if spending_df is not None and not spending_df.empty:
            results['spending_analysis'] = self._analyze_spending(spending_df)

        # Process contracts
        if contracts_df is not None and not contracts_df.empty:
            results['contracts_analysis'] = self._analyze_contracts(contracts_df)

        # Cross-reference analysis
        if len(results) > 1:
            results['military_cross_reference'] = self._cross_reference_military(results)

        return results

    def _analyze_adverse_events(self, df):
        """Analyze adverse events data"""
        analysis = {}

        # Basic statistics
        analysis['total_events'] = len(df)
        analysis['unique_drugs'] = df['drug_name'].nunique() if 'drug_name' in df.columns else 0
        analysis['serious_events'] = df['serious'].eq('1').sum() if 'serious' in df.columns else 0

        # Drug-specific analysis
        if 'drug_name' in df.columns:
            drug_stats = df.groupby('drug_name').agg({
                'safetyreportid': 'count',
                'serious': lambda x: (x == '1').sum()
            }).reset_index()

            drug_stats.columns = ['drug_name', 'total_events', 'serious_events']
            drug_stats['serious_rate'] = drug_stats['serious_events'] / drug_stats['total_events']

            # Detect anomalies in adverse event rates
            if len(drug_stats) > 10:
                anomaly_features = ['total_events', 'serious_rate']
                anomalies = self.anomaly_detector.detect_anomalies(drug_stats, anomaly_features)
                drug_stats['anomaly_score'] = anomalies

            analysis['drug_statistics'] = drug_stats

        # Temporal analysis
        if 'receivedate' in df.columns:
            df['receivedate'] = pd.to_datetime(df['receivedate'], errors='coerce')
            temporal_stats = df.groupby(df['receivedate'].dt.to_period('M')).size()
            analysis['temporal_distribution'] = temporal_stats

        return analysis

    def _analyze_clinical_trials(self, df):
        """Analyze clinical trials data"""
        analysis = {}

        # Basic statistics
        analysis['total_trials'] = len(df)
        analysis['completed_trials'] = df['overall_status'].eq('Completed').sum() if 'overall_status' in df.columns else 0
        analysis['ongoing_trials'] = df['overall_status'].eq('Recruiting').sum() if 'overall_status' in df.columns else 0

        # Sponsor analysis
        if 'sponsor' in df.columns:
            sponsor_stats = df['sponsor'].value_counts().head(10)
            analysis['top_sponsors'] = sponsor_stats

        # Enrollment analysis
        if 'enrollment_count' in df.columns:
            df['enrollment_count'] = pd.to_numeric(df['enrollment_count'], errors='coerce')
            enrollment_stats = df['enrollment_count'].describe()
            analysis['enrollment_statistics'] = enrollment_stats

            # Detect anomalies in enrollment
            if len(df.dropna(subset=['enrollment_count'])) > 10:
                enrollment_data = df[['enrollment_count']].dropna()
                anomalies = self.anomaly_detector.detect_statistical_anomalies(
                    enrollment_data, 'enrollment_count', method='iqr'
                )
                analysis['enrollment_anomalies'] = anomalies.sum()

        return analysis

    def _analyze_financial_data(self, df):
        """Analyze financial data from SEC filings"""
        analysis = {}

        # Revenue and profit analysis
        if 'revenue' in df.columns and 'net_income' in df.columns:
            df['profit_margin'] = df['net_income'] / df['revenue']

            financial_stats = df[['revenue', 'net_income', 'profit_margin']].describe()
            analysis['financial_statistics'] = financial_stats

            # Detect anomalies in financial metrics
            if len(df) > 5:
                financial_features = ['revenue', 'net_income', 'profit_margin']
                anomalies = self.anomaly_detector.detect_anomalies(df, financial_features)
                analysis['financial_anomalies'] = (anomalies == -1).sum()

        return analysis

    def _analyze_payments(self, df):
        """Analyze Open Payments data"""
        analysis = {}

        # Payment statistics
        if 'payment_amount' in df.columns:
            payment_stats = df['payment_amount'].describe()
            analysis['payment_statistics'] = payment_stats

            # Top recipients
            if 'physician_name' in df.columns:
                top_recipients = df.groupby('physician_name')['payment_amount'].sum().nlargest(10)
                analysis['top_recipients'] = top_recipients

            # Payment type analysis
            if 'payment_type' in df.columns:
                payment_types = df['payment_type'].value_counts()
                analysis['payment_types'] = payment_types

            # Detect anomalies in payment amounts
            if len(df) > 10:
                anomalies = self.anomaly_detector.detect_statistical_anomalies(
                    df, 'payment_amount', method='zscore', threshold=2
                )
                analysis['payment_anomalies'] = anomalies.sum()

        return analysis

    def _analyze_spending(self, df):
        """Analyze federal spending data"""
        analysis = {}

        if 'award_amount' in df.columns:
            spending_stats = df['award_amount'].describe()
            analysis['spending_statistics'] = spending_stats

            # Top recipients
            if 'recipient_name' in df.columns:
                top_recipients = df.groupby('recipient_name')['award_amount'].sum().nlargest(10)
                analysis['top_recipients'] = top_recipients

            # Agency analysis
            if 'awarding_agency' in df.columns:
                agency_spending = df.groupby('awarding_agency')['award_amount'].sum().nlargest(10)
                analysis['agency_spending'] = agency_spending

            # Detect anomalies in award amounts
            if len(df) > 10:
                anomalies = self.anomaly_detector.detect_statistical_anomalies(
                    df, 'award_amount', method='iqr'
                )
                analysis['spending_anomalies'] = anomalies.sum()

        return analysis

    def _analyze_contracts(self, df):
        """Analyze contract data"""
        analysis = {}

        # Contract value analysis
        if 'award_amount' in df.columns:
            contract_stats = df['award_amount'].describe()
            analysis['contract_statistics'] = contract_stats

        # Contract type analysis
        if 'description' in df.columns:
            # Simple keyword analysis for contract types
            defense_keywords = ['defense', 'military', 'weapon', 'security']
            research_keywords = ['research', 'development', 'study']

            df['contract_category'] = 'other'
            df.loc[df['description'].str.lower().str.contains('|'.join(defense_keywords)), 'contract_category'] = 'defense'
            df.loc[df['description'].str.lower().str.contains('|'.join(research_keywords)), 'contract_category'] = 'research'

            category_counts = df['contract_category'].value_counts()
            analysis['contract_categories'] = category_counts

        return analysis

    def _cross_reference_analysis(self, results):
        """Cross-reference different data sources for inconsistencies"""
        cross_analysis = {}

        # Example: Check if drugs with high adverse events have corresponding clinical trials
        if 'adverse_events_analysis' in results and 'clinical_trials_analysis' in results:
            ae_analysis = results['adverse_events_analysis']
            ct_analysis = results['clinical_trials_analysis']

            if 'drug_statistics' in ae_analysis:
                drugs_with_issues = ae_analysis['drug_statistics'][
                    ae_analysis['drug_statistics']['total_events'] > 100
                ]['drug_name'].tolist()

                # Check if these drugs have clinical trials
                cross_analysis['drugs_with_trials_check'] = {
                    'problematic_drugs': drugs_with_issues,
                    'note': 'Manual review needed to verify if problematic drugs have adequate clinical trial oversight'
                }

        # Financial and payment cross-reference
        if 'financial_analysis' in results and 'payments_analysis' in results:
            fin_analysis = results['financial_analysis']
            pay_analysis = results['payments_analysis']

            if 'financial_anomalies' in fin_analysis and 'payment_anomalies' in pay_analysis:
                cross_analysis['financial_payment_correlation'] = {
                    'financial_anomalies': fin_analysis['financial_anomalies'],
                    'payment_anomalies': pay_analysis['payment_anomalies'],
                    'note': 'High anomalies in both areas may indicate coordinated issues'
                }

        return cross_analysis

    def _cross_reference_military(self, results):
        """Cross-reference military data sources"""
        cross_analysis = {}

        if 'spending_analysis' in results and 'contracts_analysis' in results:
            spending = results['spending_analysis']
            contracts = results['contracts_analysis']

            # Check for spending without contracts or vice versa
            cross_analysis['spending_contract_alignment'] = {
                'note': 'Compare spending amounts with contract values for discrepancies'
            }

        return cross_analysis

    def generate_visualizations(self, analysis_results, output_dir='visualizations'):
        """Generate visualizations for analysis results"""
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        plots = []

        # Adverse events visualization
        if 'adverse_events_analysis' in analysis_results:
            ae_analysis = analysis_results['adverse_events_analysis']

            if 'drug_statistics' in ae_analysis:
                drug_stats = ae_analysis['drug_statistics']

                plt.figure(figsize=(12, 6))
                top_drugs = drug_stats.nlargest(10, 'total_events')
                plt.bar(range(len(top_drugs)), top_drugs['total_events'])
                plt.xticks(range(len(top_drugs)), top_drugs['drug_name'], rotation=45, ha='right')
                plt.title('Top 10 Drugs by Adverse Event Reports')
                plt.ylabel('Number of Reports')
                plt.tight_layout()
                plt.savefig(f'{output_dir}/adverse_events_by_drug.png', dpi=150, bbox_inches='tight')
                plt.close()
                plots.append(f'{output_dir}/adverse_events_by_drug.png')

        # Financial visualization
        if 'financial_analysis' in analysis_results:
            fin_analysis = analysis_results['financial_analysis']

            if 'financial_statistics' in fin_analysis:
                stats = fin_analysis['financial_statistics']

                plt.figure(figsize=(10, 6))
                companies = ['Company A', 'Company B']  # Would use actual company names
                revenue = [383285000000, 211915000000]  # Would use actual data
                profit = [97000000000, 72361000000]

                x = np.arange(len(companies))
                width = 0.35

                plt.bar(x - width/2, revenue, width, label='Revenue', alpha=0.8)
                plt.bar(x + width/2, profit, width, label='Net Income', alpha=0.8)
                plt.xticks(x, companies)
                plt.title('Financial Performance Comparison')
                plt.ylabel('Amount ($)')
                plt.legend()
                plt.yscale('log')
                plt.tight_layout()
                plt.savefig(f'{output_dir}/financial_comparison.png', dpi=150, bbox_inches='tight')
                plt.close()
                plots.append(f'{output_dir}/financial_comparison.png')

        return plots

# Example usage
if __name__ == "__main__":
    processor = DataProcessor()

    # Mock data for testing
    adverse_events = pd.DataFrame({
        'drug_name': ['Drug A', 'Drug B', 'Drug A', 'Drug C'] * 25,
        'safetyreportid': range(100),
        'serious': ['1', '0', '1', '0'] * 25
    })

    clinical_trials = pd.DataFrame({
        'nct_id': [f'NCT{i}' for i in range(50)],
        'brief_title': [f'Trial {i}' for i in range(50)],
        'overall_status': ['Completed'] * 30 + ['Recruiting'] * 20,
        'enrollment_count': np.random.randint(50, 1000, 50),
        'sponsor': ['Pfizer'] * 15 + ['Merck'] * 15 + ['Other'] * 20
    })

    # Process pharma data
    pharma_results = processor.process_pharma_data(
        adverse_events_df=adverse_events,
        clinical_trials_df=clinical_trials
    )

    print("Pharma Analysis Results:")
    for key, value in pharma_results.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for subkey, subvalue in value.items():
                if isinstance(subvalue, pd.DataFrame):
                    print(f"  {subkey}: {len(subvalue)} records")
                elif isinstance(subvalue, pd.Series):
                    print(f"  {subkey}: {len(subvalue)} items")
                else:
                    print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")

    # Generate visualizations
    plots = processor.generate_visualizations(pharma_results)
    print(f"\nGenerated {len(plots)} visualization plots")