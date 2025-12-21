import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import json

Base = declarative_base()

class AdverseEvent(Base):
    __tablename__ = 'adverse_events'

    id = Column(Integer, primary_key=True)
    safetyreportid = Column(String(50), unique=True)
    receivedate = Column(String(20))
    serious = Column(String(5))
    drug_name = Column(String(200))
    drug_indication = Column(Text)
    patient_age = Column(String(20))
    patient_sex = Column(String(5))
    reaction = Column(Text)
    outcome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class ClinicalTrial(Base):
    __tablename__ = 'clinical_trials'

    id = Column(Integer, primary_key=True)
    nct_id = Column(String(20), unique=True)
    brief_title = Column(Text)
    official_title = Column(Text)
    overall_status = Column(String(50))
    phase = Column(String(50))
    enrollment_count = Column(Integer)
    sponsor = Column(String(200))
    start_date = Column(String(20))
    completion_date = Column(String(20))
    study_type = Column(String(50))
    conditions = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class SECFiling(Base):
    __tablename__ = 'sec_filings'

    id = Column(Integer, primary_key=True)
    cik = Column(String(20))
    company_name = Column(String(200))
    form_type = Column(String(20))
    filing_date = Column(String(20))
    revenue = Column(Float)
    net_income = Column(Float)
    total_assets = Column(Float)
    rd_expense = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class OpenPayment(Base):
    __tablename__ = 'open_payments'

    id = Column(Integer, primary_key=True)
    physician_name = Column(String(200))
    company_name = Column(String(200))
    payment_amount = Column(Float)
    payment_type = Column(String(100))
    payment_date = Column(String(20))
    nature_of_payment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class FederalSpending(Base):
    __tablename__ = 'federal_spending'

    id = Column(Integer, primary_key=True)
    award_id = Column(String(20), unique=True)
    recipient_name = Column(String(200))
    awarding_agency = Column(String(200))
    award_amount = Column(Float)
    award_date = Column(String(20))
    description = Column(Text)
    contract_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class WhistleblowerReport(Base):
    __tablename__ = 'whistleblower_reports'

    id = Column(Integer, primary_key=True)
    report_id = Column(String(20), unique=True)
    source = Column(String(100))
    category = Column(String(100))
    description = Column(Text)
    company_involved = Column(String(200))
    amount_involved = Column(Float, nullable=True)
    date_reported = Column(String(20))
    severity = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditAlert(Base):
    __tablename__ = 'audit_alerts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    guardian = Column(String(50))
    alert_type = Column(String(100))
    severity = Column(String(20))
    description = Column(Text)
    data_point = Column(Text)  # JSON string
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

class DatabaseManager:
    def __init__(self, db_path='guardian_os_audit.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

    def insert_adverse_events(self, df):
        """Insert adverse events data"""
        session = self.get_session()
        try:
            records = []
            for _, row in df.iterrows():
                # Handle nested drug data
                drug_name = ""
                if 'patient' in row and 'drug' in row['patient']:
                    drugs = row['patient']['drug']
                    if isinstance(drugs, list) and len(drugs) > 0:
                        drug_name = drugs[0].get('medicinalproduct', '')

                record = AdverseEvent(
                    safetyreportid=str(row.get('safetyreportid', '')),
                    receivedate=str(row.get('receivedate', '')),
                    serious=str(row.get('serious', '')),
                    drug_name=drug_name,
                    drug_indication=str(row.get('drug_indication', '')),
                    patient_age=str(row.get('patient', {}).get('patientonsetage', '')),
                    patient_sex=str(row.get('patient', {}).get('patientsex', '')),
                    reaction=json.dumps(row.get('patient', {}).get('reaction', [])),
                    outcome=str(row.get('patient', {}).get('reaction', [{}])[0].get('reactionoutcome', ''))
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} adverse event records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting adverse events: {e}")
        finally:
            session.close()

    def insert_clinical_trials(self, df):
        """Insert clinical trials data"""
        session = self.get_session()
        try:
            records = []
            for _, row in df.iterrows():
                record = ClinicalTrial(
                    nct_id=str(row.get('nct_id', '')),
                    brief_title=str(row.get('brief_title', '')),
                    official_title=str(row.get('official_title', '')),
                    overall_status=str(row.get('overall_status', '')),
                    phase=json.dumps(row.get('phase', [])),
                    enrollment_count=int(row.get('enrollment_count', 0)) if pd.notna(row.get('enrollment_count')) else None,
                    sponsor=str(row.get('sponsor', '')),
                    start_date=str(row.get('start_date', '')),
                    completion_date=str(row.get('completion_date', '')),
                    study_type=str(row.get('study_type', '')),
                    conditions=json.dumps(row.get('conditions', []))
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} clinical trial records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting clinical trials: {e}")
        finally:
            session.close()

    def insert_sec_filings(self, df):
        """Insert SEC filings data"""
        session = self.get_session()
        try:
            records = []
            for _, row in df.iterrows():
                record = SECFiling(
                    cik=str(row.get('cik', '')),
                    company_name=str(row.get('company_name', '')),
                    form_type=str(row.get('form_type', '')),
                    filing_date=str(row.get('filing_date', '')),
                    revenue=float(row.get('revenue', 0)) if pd.notna(row.get('revenue')) else None,
                    net_income=float(row.get('net_income', 0)) if pd.notna(row.get('net_income')) else None,
                    total_assets=float(row.get('total_assets', 0)) if pd.notna(row.get('total_assets')) else None,
                    rd_expense=float(row.get('rd_expense', 0)) if pd.notna(row.get('rd_expense')) else None
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} SEC filing records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting SEC filings: {e}")
        finally:
            session.close()

    def insert_open_payments(self, df):
        """Insert Open Payments data"""
        session = self.get_session()
        try:
            records = []
            for _, row in df.iterrows():
                record = OpenPayment(
                    physician_name=str(row.get('physician_name', '')),
                    company_name=str(row.get('company_name', '')),
                    payment_amount=float(row.get('payment_amount', 0)) if pd.notna(row.get('payment_amount')) else None,
                    payment_type=str(row.get('payment_type', '')),
                    payment_date=str(row.get('payment_date', '')),
                    nature_of_payment=str(row.get('nature_of_payment', ''))
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} Open Payment records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting Open Payments: {e}")
        finally:
            session.close()

    def insert_federal_spending(self, df):
        """Insert federal spending data"""
        session = self.get_session()
        try:
            records = []
            for _, row in df.iterrows():
                record = FederalSpending(
                    award_id=str(row.get('award_id', '')),
                    recipient_name=str(row.get('recipient_name', '')),
                    awarding_agency=str(row.get('awarding_agency', '')),
                    award_amount=float(row.get('award_amount', 0)) if pd.notna(row.get('award_amount')) else None,
                    award_date=str(row.get('award_date', '')),
                    description=str(row.get('description', '')),
                    contract_type=str(row.get('contract_type', ''))
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} federal spending records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting federal spending: {e}")
        finally:
            session.close()

    def insert_whistleblower_reports(self, df):
        """Insert whistleblower reports"""
        session = self.get_session()
        try:
            records = []
            for _, row in df.iterrows():
                record = WhistleblowerReport(
                    report_id=str(row.get('report_id', '')),
                    source=str(row.get('source', '')),
                    category=str(row.get('category', '')),
                    description=str(row.get('description', '')),
                    company_involved=str(row.get('company_involved', '')),
                    amount_involved=float(row.get('amount_involved', 0)) if pd.notna(row.get('amount_involved')) else None,
                    date_reported=str(row.get('date_reported', '')),
                    severity=str(row.get('severity', ''))
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} whistleblower report records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting whistleblower reports: {e}")
        finally:
            session.close()

    def insert_audit_alerts(self, alerts):
        """Insert audit alerts"""
        session = self.get_session()
        try:
            records = []
            for alert in alerts:
                record = AuditAlert(
                    guardian=alert.get('guardian', ''),
                    alert_type=alert.get('type', ''),
                    severity=alert.get('severity', ''),
                    description=alert.get('description', ''),
                    data_point=json.dumps(alert.get('data_point', {}))
                )
                records.append(record)

            session.add_all(records)
            session.commit()
            print(f"Inserted {len(records)} audit alert records")

        except Exception as e:
            session.rollback()
            print(f"Error inserting audit alerts: {e}")
        finally:
            session.close()

    def load_data(self, table_name, limit=None):
        """Load data from a specific table"""
        session = self.get_session()
        try:
            if table_name == 'adverse_events':
                query = session.query(AdverseEvent)
            elif table_name == 'clinical_trials':
                query = session.query(ClinicalTrial)
            elif table_name == 'sec_filings':
                query = session.query(SECFiling)
            elif table_name == 'open_payments':
                query = session.query(OpenPayment)
            elif table_name == 'federal_spending':
                query = session.query(FederalSpending)
            elif table_name == 'whistleblower_reports':
                query = session.query(WhistleblowerReport)
            elif table_name == 'audit_alerts':
                query = session.query(AuditAlert)
            else:
                raise ValueError(f"Unknown table: {table_name}")

            if limit:
                query = query.limit(limit)

            results = query.all()

            # Convert to DataFrame
            if results:
                data = []
                for result in results:
                    data.append({column.name: getattr(result, column.name) for column in result.__table__.columns})
                return pd.DataFrame(data)
            else:
                return pd.DataFrame()

        except Exception as e:
            print(f"Error loading data from {table_name}: {e}")
            return pd.DataFrame()
        finally:
            session.close()

    def get_table_stats(self):
        """Get statistics for all tables"""
        session = self.get_session()
        stats = {}

        try:
            tables = [
                ('adverse_events', AdverseEvent),
                ('clinical_trials', ClinicalTrial),
                ('sec_filings', SECFiling),
                ('open_payments', OpenPayment),
                ('federal_spending', FederalSpending),
                ('whistleblower_reports', WhistleblowerReport),
                ('audit_alerts', AuditAlert)
            ]

            for table_name, table_class in tables:
                count = session.query(table_class).count()
                stats[table_name] = count

        except Exception as e:
            print(f"Error getting table stats: {e}")
        finally:
            session.close()

        return stats

    def clear_table(self, table_name):
        """Clear all data from a table"""
        session = self.get_session()
        try:
            if table_name == 'adverse_events':
                session.query(AdverseEvent).delete()
            elif table_name == 'clinical_trials':
                session.query(ClinicalTrial).delete()
            elif table_name == 'sec_filings':
                session.query(SECFiling).delete()
            elif table_name == 'open_payments':
                session.query(OpenPayment).delete()
            elif table_name == 'federal_spending':
                session.query(FederalSpending).delete()
            elif table_name == 'whistleblower_reports':
                session.query(WhistleblowerReport).delete()
            elif table_name == 'audit_alerts':
                session.query(AuditAlert).delete()

            session.commit()
            print(f"Cleared all data from {table_name}")

        except Exception as e:
            session.rollback()
            print(f"Error clearing table {table_name}: {e}")
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()

    # Test loading some mock data
    print("Database tables created successfully!")

    # Show table statistics
    stats = db.get_table_stats()
    print("\nTable Statistics:")
    for table, count in stats.items():
        print(f"{table}: {count} records")