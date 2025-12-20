import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict

def generate_corruption_visualizations():
    """Generate visualizations for banking corruption audit findings"""

    conn = sqlite3.connect('reality_audit.db')
    c = conn.cursor()

    # Get all evidence
    c.execute("SELECT timestamp, source, content, verification_hash FROM evidence_log ORDER BY timestamp")
    evidence = c.fetchall()

    if not evidence:
        print("No evidence data found for visualization")
        return

    # Process data for visualization
    sources = defaultdict(int)
    severity_levels = defaultdict(int)
    timeline_data = defaultdict(int)

    for timestamp, source, content, verification_hash in evidence:
        # Count by source
        sources[source] += 1

        # Extract severity from verification_hash
        if verification_hash.startswith("SEVERITY_"):
            severity = int(verification_hash.split("_")[1])
            severity_levels[severity] += 1

        # Timeline data (by day)
        try:
            date = datetime.fromisoformat(timestamp).date()
            timeline_data[str(date)] += 1
        except:
            pass

    # Create visualizations
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Banking Corruption Audit Findings', fontsize=16, fontweight='bold')

    # 1. Evidence by Source
    if sources:
        ax1.bar(range(len(sources)), list(sources.values()))
        ax1.set_xticks(range(len(sources)))
        ax1.set_xticklabels([s.replace('https://www.', '').replace('https://', '') for s in sources.keys()],
                           rotation=45, ha='right')
        ax1.set_title('Evidence Distribution by Source')
        ax1.set_ylabel('Number of Findings')

    # 2. Severity Distribution
    if severity_levels:
        severities = sorted(severity_levels.keys())
        counts = [severity_levels[s] for s in severities]
        ax2.bar(severities, counts, color=['green', 'yellow', 'orange', 'red'])
        ax2.set_title('Corruption Severity Distribution')
        ax2.set_xlabel('Severity Level')
        ax2.set_ylabel('Number of Cases')
        ax2.set_xticks(severities)

    # 3. Timeline of Findings
    if timeline_data:
        dates = sorted(timeline_data.keys())
        counts = [timeline_data[d] for d in dates]
        ax3.plot(dates, counts, marker='o', linestyle='-', color='blue')
        ax3.set_title('Audit Findings Timeline')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Findings per Day')
        ax3.tick_params(axis='x', rotation=45)

    # 4. Corruption Types Breakdown (from content analysis)
    corruption_types = defaultdict(int)
    for _, _, content, _ in evidence:
        if "CORRUPTION:" in content:
            # Extract corruption types from content
            types = [line.split(": ")[1] for line in content.split(", ") if "CORRUPTION:" in line]
            for corruption_type in types:
                corruption_types[corruption_type] += 1

    if corruption_types:
        types = list(corruption_types.keys())[:10]  # Top 10
        counts = [corruption_types[t] for t in types]
        ax4.barh(types, counts, color='darkred')
        ax4.set_title('Top Corruption Types Detected')
        ax4.set_xlabel('Frequency')

    plt.tight_layout()
    plt.savefig('banking_corruption_audit_report.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Generate summary statistics
    total_findings = len(evidence)
    avg_severity = sum(severity_levels.keys()) / len(severity_levels) if severity_levels else 0
    most_active_source = max(sources.items(), key=lambda x: x[1]) if sources else ("None", 0)

    print("
=== BANKING CORRUPTION AUDIT STATISTICS ===")
    print(f"Total Findings: {total_findings}")
    print(".2f")
    print(f"Most Active Source: {most_active_source[0]} ({most_active_source[1]} findings)")
    print(f"Visualization saved as: banking_corruption_audit_report.png")

    conn.close()

if __name__ == "__main__":
    generate_corruption_visualizations()