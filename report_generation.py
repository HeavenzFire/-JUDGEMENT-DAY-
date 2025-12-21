import pandas as pd
from datetime import datetime, timedelta
import json
from database_setup import DatabaseManager
from data_processing import DataProcessor
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

class ReportGenerator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.data_processor = DataProcessor()
        self.styles = getSampleStyleSheet()

        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        )

    def generate_comprehensive_report(self, output_file='guardian_os_audit_report.pdf'):
        """Generate comprehensive audit report"""
        print(f"Generating comprehensive audit report: {output_file}")

        # Create PDF document
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        elements = []

        # Title page
        elements.extend(self._create_title_page())

        # Executive summary
        elements.extend(self._create_executive_summary())

        # Data overview
        elements.extend(self._create_data_overview())

        # Guardian alerts summary
        elements.extend(self._create_alerts_summary())

        # Detailed findings
        elements.extend(self._create_detailed_findings())

        # Recommendations
        elements.extend(self._create_recommendations())

        # Build PDF
        doc.build(elements)
        print(f"Report generated: {output_file}")

        return output_file

    def _create_title_page(self):
        """Create title page elements"""
        elements = []

        # Title
        title = Paragraph("🛡️ Guardian OS Audit Report", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))

        # Subtitle
        subtitle = Paragraph("Big Pharma & Military Sector Compliance Audit", self.styles['Heading2'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))

        # Report info
        report_info = f"""
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Analysis Period:</b> Last 30 days<br/>
        <b>System Version:</b> Guardian OS v1.0<br/>
        <b>Confidential:</b> For authorized personnel only
        """

        elements.append(Paragraph(report_info, self.styles['Normal']))
        elements.append(Spacer(1, 1*inch))

        # Disclaimer
        disclaimer = """
        <b>Disclaimer:</b> This report contains sensitive information related to compliance
        monitoring and risk assessment. Distribution is restricted to authorized personnel
        with appropriate security clearance.
        """
        elements.append(Paragraph(disclaimer, self.styles['Italic']))
        elements.append(Spacer(1, 2*inch))

        return elements

    def _create_executive_summary(self):
        """Create executive summary section"""
        elements = []

        elements.append(Paragraph("Executive Summary", self.section_style))

        # Get summary statistics
        db_stats = self.db_manager.get_table_stats()
        alerts_df = self.db_manager.load_data('audit_alerts', limit=1000)

        total_records = sum(db_stats.values())
        total_alerts = len(alerts_df) if not alerts_df.empty else 0

        # Severity breakdown
        severity_counts = {}
        if not alerts_df.empty:
            severity_counts = alerts_df['severity'].value_counts().to_dict()

        summary_text = f"""
        The Guardian OS audit system has analyzed <b>{total_records:,}</b> records across
        pharmaceutical and military sectors. The automated monitoring identified
        <b>{total_alerts}</b> compliance and risk alerts during the reporting period.

        <b>Key Findings:</b><br/>
        • Critical Issues: {severity_counts.get('critical', 0)}<br/>
        • High Priority: {severity_counts.get('high', 0)}<br/>
        • Medium Priority: {severity_counts.get('medium', 0)}<br/>
        • Low Priority: {severity_counts.get('low', 0)}<br/>

        The system successfully monitored regulatory compliance, ethical standards,
        transparency requirements, and data security across both sectors.
        """

        elements.append(Paragraph(summary_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))

        return elements

    def _create_data_overview(self):
        """Create data overview section"""
        elements = []

        elements.append(Paragraph("Data Sources Overview", self.section_style))

        # Get database statistics
        db_stats = self.db_manager.get_table_stats()

        # Create data table
        data = [['Data Source', 'Records', 'Status']]
        data.extend([
            ['FDA Adverse Events', f"{db_stats.get('adverse_events', 0):,}", 'Active'],
            ['Clinical Trials', f"{db_stats.get('clinical_trials', 0):,}", 'Active'],
            ['SEC Filings', f"{db_stats.get('sec_filings', 0):,}", 'Active'],
            ['Open Payments', f"{db_stats.get('open_payments', 0):,}", 'Active'],
            ['Federal Spending', f"{db_stats.get('federal_spending', 0):,}", 'Active'],
            ['Whistleblower Reports', f"{db_stats.get('whistleblower_reports', 0):,}", 'Limited'],
            ['Audit Alerts', f"{db_stats.get('audit_alerts', 0):,}", 'Active']
        ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))

        # Data quality summary
        quality_text = """
        <b>Data Quality Assessment:</b><br/>
        • All primary data sources are actively monitored and updated<br/>
        • Real-time ingestion pipelines ensure data freshness<br/>
        • Automated validation checks maintain data integrity<br/>
        • Cross-referencing between sources enables comprehensive analysis
        """

        elements.append(Paragraph(quality_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))

        return elements

    def _create_alerts_summary(self):
        """Create alerts summary section"""
        elements = []

        elements.append(Paragraph("Guardian Alerts Summary", self.section_style))

        # Get alerts data
        alerts_df = self.db_manager.load_data('audit_alerts', limit=1000)

        if alerts_df.empty:
            elements.append(Paragraph("No alerts recorded in the reporting period.", self.styles['Normal']))
            return elements

        # Guardian breakdown
        guardian_counts = alerts_df['guardian'].value_counts()

        # Create alerts table
        alert_data = [['Guardian', 'Total Alerts', 'Critical', 'High', 'Medium', 'Low']]

        for guardian in guardian_counts.index:
            guardian_alerts = alerts_df[alerts_df['guardian'] == guardian]
            severity_counts = guardian_alerts['severity'].value_counts()

            row = [
                guardian,
                len(guardian_alerts),
                severity_counts.get('critical', 0),
                severity_counts.get('high', 0),
                severity_counts.get('medium', 0),
                severity_counts.get('low', 0)
            ]
            alert_data.append(row)

        table = Table(alert_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))

        # Top alerts
        elements.append(Paragraph("Top Critical Alerts", self.styles['Heading3']))

        critical_alerts = alerts_df[alerts_df['severity'] == 'critical'].head(5)
        if not critical_alerts.empty:
            for _, alert in critical_alerts.iterrows():
                alert_text = f"<b>{alert['guardian']}:</b> {alert['description']}"
                elements.append(Paragraph(alert_text, self.styles['Bullet']))
                elements.append(Spacer(1, 0.1*inch))

        return elements

    def _create_detailed_findings(self):
        """Create detailed findings section"""
        elements = []

        elements.append(Paragraph("Detailed Findings", self.section_style))

        # Load and process data for analysis
        adverse_events = self.db_manager.load_data('adverse_events', limit=1000)
        clinical_trials = self.db_manager.load_data('clinical_trials', limit=1000)
        federal_spending = self.db_manager.load_data('federal_spending', limit=1000)

        # Pharmaceutical findings
        if not adverse_events.empty:
            elements.append(Paragraph("Pharmaceutical Sector Findings", self.styles['Heading3']))

            pharma_analysis = self.data_processor.process_pharma_data(
                adverse_events_df=adverse_events,
                clinical_trials_df=clinical_trials
            )

            if 'adverse_events_analysis' in pharma_analysis:
                ae_analysis = pharma_analysis['adverse_events_analysis']
                findings_text = f"""
                <b>Adverse Events Analysis:</b><br/>
                • Total adverse events: {ae_analysis.get('total_events', 0):,}<br/>
                • Unique drugs monitored: {ae_analysis.get('unique_drugs', 0)}<br/>
                • Serious events: {ae_analysis.get('serious_events', 0):,}<br/>
                """

                if 'drug_statistics' in ae_analysis:
                    drug_stats = ae_analysis['drug_statistics']
                    high_risk_drugs = drug_stats[drug_stats['total_events'] > 50]
                    if not high_risk_drugs.empty:
                        findings_text += f"• High-risk drugs (>50 events): {len(high_risk_drugs)} identified<br/>"

                elements.append(Paragraph(findings_text, self.styles['Normal']))

        # Military findings
        if not federal_spending.empty:
            elements.append(Paragraph("Military Sector Findings", self.styles['Heading3']))

            military_analysis = self.data_processor.process_military_data(
                spending_df=federal_spending
            )

            if 'spending_analysis' in military_analysis:
                spending_analysis = military_analysis['spending_analysis']
                findings_text = f"""
                <b>Federal Spending Analysis:</b><br/>
                • Total contracts analyzed: {len(federal_spending):,}<br/>
                • Total spending: ${federal_spending['award_amount'].sum():,.0f}<br/>
                • Average contract value: ${federal_spending['award_amount'].mean():,.0f}<br/>
                """

                if 'spending_anomalies' in spending_analysis:
                    anomalies = spending_analysis['spending_anomalies']
                    findings_text += f"• Spending anomalies detected: {anomalies}<br/>"

                elements.append(Paragraph(findings_text, self.styles['Normal']))

        return elements

    def _create_recommendations(self):
        """Create recommendations section"""
        elements = []

        elements.append(Paragraph("Recommendations", self.section_style))

        recommendations = [
            "Implement automated alert escalation for critical compliance violations",
            "Expand data sources to include additional regulatory databases and whistleblower platforms",
            "Develop predictive analytics to identify emerging compliance risks",
            "Establish regular stakeholder reporting and transparency dashboards",
            "Conduct periodic system audits and guardian effectiveness reviews",
            "Integrate with existing regulatory systems for seamless compliance monitoring",
            "Develop training programs for personnel on system capabilities and findings interpretation",
            "Establish partnerships with regulatory agencies for enhanced data access and validation"
        ]

        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['Bullet']))
            elements.append(Spacer(1, 0.05*inch))

        elements.append(Spacer(1, 0.5*inch))

        # Next steps
        elements.append(Paragraph("Next Steps", self.styles['Heading3']))

        next_steps = [
            "Schedule quarterly comprehensive audits using Guardian OS",
            "Review and update guardian thresholds based on regulatory changes",
            "Expand pilot program to additional pharmaceutical and defense contractors",
            "Develop mobile application for field auditors and inspectors",
            "Establish continuous monitoring protocols for high-risk areas"
        ]

        for step in next_steps:
            elements.append(Paragraph(f"• {step}", self.styles['Bullet']))
            elements.append(Spacer(1, 0.05*inch))

        return elements

    def generate_excel_report(self, output_file='guardian_os_audit_report.xlsx'):
        """Generate Excel report with detailed data"""
        print(f"Generating Excel report: {output_file}")

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            db_stats = self.db_manager.get_table_stats()
            alerts_df = self.db_manager.load_data('audit_alerts', limit=5000)

            summary_data = {
                'Metric': ['Total Records', 'Total Alerts', 'Critical Alerts', 'High Alerts',
                          'Medium Alerts', 'Low Alerts', 'Data Sources'],
                'Value': [
                    sum(db_stats.values()),
                    len(alerts_df) if not alerts_df.empty else 0,
                    len(alerts_df[alerts_df['severity'] == 'critical']) if not alerts_df.empty else 0,
                    len(alerts_df[alerts_df['severity'] == 'high']) if not alerts_df.empty else 0,
                    len(alerts_df[alerts_df['severity'] == 'medium']) if not alerts_df.empty else 0,
                    len(alerts_df[alerts_df['severity'] == 'low']) if not alerts_df.empty else 0,
                    len([k for k, v in db_stats.items() if v > 0])
                ]
            }

            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Data sources sheet
            data_sources = pd.DataFrame(list(db_stats.items()), columns=['Source', 'Records'])
            data_sources.to_excel(writer, sheet_name='Data_Sources', index=False)

            # Alerts sheet
            if not alerts_df.empty:
                alerts_df.to_excel(writer, sheet_name='Alerts', index=False)

            # Detailed analysis sheets
            adverse_events = self.db_manager.load_data('adverse_events', limit=5000)
            if not adverse_events.empty:
                adverse_events.to_excel(writer, sheet_name='Adverse_Events', index=False)

            clinical_trials = self.db_manager.load_data('clinical_trials', limit=5000)
            if not clinical_trials.empty:
                clinical_trials.to_excel(writer, sheet_name='Clinical_Trials', index=False)

            federal_spending = self.db_manager.load_data('federal_spending', limit=5000)
            if not federal_spending.empty:
                federal_spending.to_excel(writer, sheet_name='Federal_Spending', index=False)

        print(f"Excel report generated: {output_file}")
        return output_file

    def generate_json_report(self, output_file='guardian_os_audit_report.json'):
        """Generate JSON report for API consumption"""
        print(f"Generating JSON report: {output_file}")

        # Collect all data
        report_data = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'system_version': 'Guardian OS v1.0',
                'report_type': 'Comprehensive Audit Report'
            },
            'data_summary': self.db_manager.get_table_stats(),
            'alerts': []
        }

        # Get alerts
        alerts_df = self.db_manager.load_data('audit_alerts', limit=1000)
        if not alerts_df.empty:
            report_data['alerts'] = alerts_df.to_dict('records')

        # Add analysis summaries
        adverse_events = self.db_manager.load_data('adverse_events', limit=1000)
        if not adverse_events.empty:
            pharma_analysis = self.data_processor.process_pharma_data(adverse_events_df=adverse_events)
            report_data['pharma_analysis'] = pharma_analysis

        federal_spending = self.db_manager.load_data('federal_spending', limit=1000)
        if not federal_spending.empty:
            military_analysis = self.data_processor.process_military_data(spending_df=federal_spending)
            report_data['military_analysis'] = military_analysis

        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"JSON report generated: {output_file}")
        return output_file

# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()

    # Generate comprehensive PDF report
    pdf_report = generator.generate_comprehensive_report()

    # Generate Excel report
    excel_report = generator.generate_excel_report()

    # Generate JSON report
    json_report = generator.generate_json_report()

    print("All reports generated successfully!")