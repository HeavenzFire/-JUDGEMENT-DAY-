import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from database_setup import DatabaseManager

class DataIngestion:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Guardian-OS-Audit/1.0 (Research Project)'
        })

    def fetch_fda_adverse_events(self, limit=1000, drug_name=None):
        """Fetch adverse events data from FDA API"""
        base_url = "https://api.fda.gov/drug/event.json"

        params = {
            'limit': min(limit, 1000),  # FDA API limit is 1000
            'sort': 'receivedate:desc'
        }

        if drug_name:
            params['search'] = f'patient.drug.medicinalproduct:"{drug_name}"'

        try:
            print(f"Fetching FDA adverse events data...")
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if 'results' in data:
                df = pd.json_normalize(data['results'])
                print(f"Retrieved {len(df)} adverse event records")
                return df
            else:
                print("No results found in FDA response")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error fetching FDA data: {e}")
            return pd.DataFrame()

    def fetch_clinical_trials(self, limit=1000, condition=None):
        """Fetch clinical trials data from ClinicalTrials.gov API"""
        base_url = "https://clinicaltrials.gov/api/v2/studies"

        params = {
            'format': 'json',
            'pageSize': min(limit, 1000),
            'sort': '@relevance'
        }

        if condition:
            params['query.cond'] = condition

        try:
            print(f"Fetching clinical trials data...")
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if 'studies' in data:
                df = pd.json_normalize(data['studies'])
                print(f"Retrieved {len(df)} clinical trial records")
                return df
            else:
                print("No results found in ClinicalTrials.gov response")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error fetching clinical trials data: {e}")
            return pd.DataFrame()

    def fetch_sec_filings(self, cik=None, limit=100):
        """Fetch SEC filings data"""
        # Note: SEC API has limitations, using sample data for demonstration
        print("SEC API access requires special registration. Using sample data...")

        # Generate sample SEC data
        companies = [
            {'cik': '0000320193', 'company_name': 'Apple Inc.', 'revenue': 383285000000, 'net_income': 97000000000},
            {'cik': '0000789019', 'company_name': 'Microsoft Corporation', 'revenue': 211915000000, 'net_income': 72361000000},
            {'cik': '0000200406', 'company_name': 'Pfizer Inc.', 'revenue': 100330000000, 'net_income': 31370000000},
            {'cik': '0000318154', 'company_name': 'Merck & Co., Inc.', 'revenue': 60714000000, 'net_income': 14940000000}
        ]

        df = pd.DataFrame(companies)
        df['form_type'] = '10-K'
        df['filing_date'] = '2024-01-01'
        df['rd_expense'] = df['revenue'] * 0.1  # Estimate R&D as 10% of revenue
        df['total_assets'] = df['revenue'] * 2  # Estimate total assets

        return df.head(limit)

    def fetch_federal_spending(self, limit=1000):
        """Fetch federal spending data from USAspending.gov"""
        # Note: USAspending.gov API is complex, using sample data for demonstration
        print("Fetching federal spending data (sample)...")

        agencies = ['Department of Defense', 'Department of Health and Human Services',
                   'Department of Veterans Affairs', 'Department of Homeland Security']

        recipients = ['Lockheed Martin', 'Raytheon Technologies', 'Boeing', 'Northrop Grumman',
                     'General Dynamics', 'Pfizer Inc.', 'Johnson & Johnson', 'Merck & Co.']

        data = []
        for i in range(limit):
            data.append({
                'award_id': f'AWARD{i:06d}',
                'recipient_name': recipients[i % len(recipients)],
                'awarding_agency': agencies[i % len(agencies)],
                'award_amount': 500000 + (i * 10000) % 5000000,  # Random amounts between 500k-5M
                'award_date': (datetime.now() - timedelta(days=i % 365)).strftime('%Y-%m-%d'),
                'description': f'Defense contract {i}' if i % 2 == 0 else f'Medical research {i}',
                'contract_type': 'DO' if i % 3 == 0 else 'IDV'
            })

        df = pd.DataFrame(data)
        print(f"Generated {len(df)} federal spending records")
        return df

    def fetch_open_payments(self, limit=1000):
        """Fetch Open Payments data"""
        # Note: CMS Open Payments API requires registration, using sample data
        print("Fetching Open Payments data (sample)...")

        physicians = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Jones']
        companies = ['Pfizer Inc.', 'Johnson & Johnson', 'Merck & Co.', 'AstraZeneca', 'Bristol Myers Squibb']

        data = []
        for i in range(limit):
            data.append({
                'physician_name': physicians[i % len(physicians)],
                'company_name': companies[i % len(companies)],
                'payment_amount': 100 + (i * 50) % 50000,  # Random payments
                'payment_type': ['Consulting', 'Speakers Bureau', 'Food and Beverage', 'Travel'][i % 4],
                'payment_date': (datetime.now() - timedelta(days=i % 365)).strftime('%Y-%m-%d'),
                'nature_of_payment': f'Payment for {["consulting", "speaking", "meal", "travel"][i % 4]} services',
            })

        df = pd.DataFrame(data)
        print(f"Generated {len(df)} Open Payments records")
        return df

    def ingest_all_data(self, limit_per_source=1000):
        """Ingest data from all sources"""
        print("Starting data ingestion from all sources...")

        # Clear existing data (optional - comment out if you want to append)
        print("Clearing existing data...")
        for table in ['adverse_events', 'clinical_trials', 'sec_filings', 'open_payments', 'federal_spending']:
            self.db_manager.clear_table(table)

        # Ingest adverse events
        print("\n1. Ingesting FDA adverse events...")
        ae_data = self.fetch_fda_adverse_events(limit=limit_per_source)
        if not ae_data.empty:
            self.db_manager.insert_adverse_events(ae_data)

        # Ingest clinical trials
        print("\n2. Ingesting clinical trials...")
        ct_data = self.fetch_clinical_trials(limit=limit_per_source)
        if not ct_data.empty:
            self.db_manager.insert_clinical_trials(ct_data)

        # Ingest SEC filings
        print("\n3. Ingesting SEC filings...")
        sec_data = self.fetch_sec_filings(limit=min(limit_per_source, 100))
        if not sec_data.empty:
            self.db_manager.insert_sec_filings(sec_data)

        # Ingest Open Payments
        print("\n4. Ingesting Open Payments...")
        op_data = self.fetch_open_payments(limit=limit_per_source)
        if not op_data.empty:
            self.db_manager.insert_open_payments(op_data)

        # Ingest federal spending
        print("\n5. Ingesting federal spending...")
        fs_data = self.fetch_federal_spending(limit=limit_per_source)
        if not fs_data.empty:
            self.db_manager.insert_federal_spending(fs_data)

        # Show final stats
        final_stats = self.db_manager.get_table_stats()
        print("
📊 Final Data Ingestion Summary:"        total_records = sum(final_stats.values())
        print(f"Total records ingested: {total_records}")
        for table, count in final_stats.items():
            print(f"  {table}: {count} records")

        return final_stats

    def update_data(self, source, days_back=7):
        """Update data from specific source for recent period"""
        print(f"Updating {source} data for last {days_back} days...")

        if source == 'adverse_events':
            # Fetch recent adverse events
            ae_data = self.fetch_fda_adverse_events(limit=500)
            if not ae_data.empty:
                self.db_manager.insert_adverse_events(ae_data)
                print(f"Updated {len(ae_data)} adverse event records")

        elif source == 'federal_spending':
            # Fetch recent spending data
            fs_data = self.fetch_federal_spending(limit=500)
            if not fs_data.empty:
                self.db_manager.insert_federal_spending(fs_data)
                print(f"Updated {len(fs_data)} federal spending records")

        else:
            print(f"Update not implemented for source: {source}")

# Example usage
if __name__ == "__main__":
    ingestion = DataIngestion()

    # Full data ingestion
    stats = ingestion.ingest_all_data(limit_per_source=500)

    # Update specific data source
    # ingestion.update_data('adverse_events', days_back=1)