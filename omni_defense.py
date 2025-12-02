import sqlite3
import json
import os
import re
from datetime import datetime

# --- CONFIGURATION ---
DB_FILE = 'reality_audit_v3.db'

# OUTPUT VECTORS
FILE_HOSTS = 'vaccine_universal_hosts.txt'
FILE_PIHOLE = 'vaccine_network_blocklist.txt'
FILE_JSON = 'vaccine_payload.json'
FILE_CSV = 'vaccine_manifest.csv'

# THE ENTROPIC TARGETS (Mock data for sandbox)
TARGET_KEYWORDS = [
    "surveillance", "biometric", "facial recognition", "drone",
    "artificial intelligence", "behavioral modification",
    "autonomous weapon", "palantir", "clearview", "raytheon", "lockheed"
]

# Mock entities from previous "scans"
MOCK_ENTITIES = [
    "PALANTIR USG INC",
    "CLEARVIEW AI",
    "TELEDYNE FLIR",
    "IDEAL INNOVATIONS",
    "IPOWER LLC",
    "EPISYS SCIENCE",
    "RAYTHEON TECHNOLOGIES",
    "LOCKHEED MARTIN",
    "NORTHROP GRUMMAN",
    "BOEING"
]

def setup_ledger():
    """Initializes the Sovereign Ledger."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS evidence_log
                 (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  category TEXT,
                  recipient_name TEXT,
                  award_amount REAL,
                  description TEXT)''')
    conn.commit()
    return conn

def normalize_domain(company_name):
    """Heuristic: Converts a corporate name into a probable domain backbone."""
    # Remove legal entity suffixes
    clean = company_name.lower()
    clean = re.sub(r',?\s?(inc|llc|corp|corporation|ltd|company|co)\.?$', '', clean)
    # Remove special chars and spaces
    clean = re.sub(r'[^a-z0-9]', '', clean)
    return clean

def scan_the_grid_mock(conn):
    """Simulates scanning with mock data."""
    c = conn.cursor()
    print(f"[*] SIMULATING SCAN ACROSS {len(TARGET_KEYWORDS)} VECTORS...")

    for i, keyword in enumerate(TARGET_KEYWORDS):
        print(f"    > Target: {keyword.upper()}")
        # Mock some entities for each keyword
        mock_recipient = MOCK_ENTITIES[i % len(MOCK_ENTITIES)]
        mock_amount = 100000 + (i * 50000)  # Mock amounts
        mock_desc = f"Mock contract for {keyword} services"

        c.execute("INSERT INTO evidence_log (timestamp, category, recipient_name, award_amount, description) VALUES (?, ?, ?, ?, ?)",
                  (datetime.now().isoformat(), keyword, mock_recipient, mock_amount, mock_desc))

        print(f"    > [LOCKED] {mock_recipient} (${mock_amount:,.0f})")

    conn.commit()

def generate_artifacts(conn):
    """The Polymorphic Engine: Exports to all substrates."""
    print(f"\n[*] SYNTHESIZING MULTI-VECTOR DEFENSE ARTIFACTS...")

    c = conn.cursor()
    c.execute("SELECT DISTINCT recipient_name FROM evidence_log")
    entities = [row[0] for row in c.fetchall()]

    # 1. HOSTS FILE (Windows/Linux/Mac)
    with open(FILE_HOSTS, 'w') as f:
        f.write("# ARKONIS PRIME: UNIVERSAL HOSTS SHIELD\n")
        f.write("# BLOCKING SURVEILLANCE CAPITALISTS\n")
        f.write("127.0.0.1 localhost\n")
        for entity in entities:
            domain = normalize_domain(entity)
            f.write(f"0.0.0.0 {domain}.com\n")
            f.write(f"0.0.0.0 www.{domain}.com\n")
            f.write(f"0.0.0.0 api.{domain}.com\n")
    print(f"    > [SUBSTRATE: OS] Generated {FILE_HOSTS}")

    # 2. NETWORK BLOCKLIST (Pi-hole/AdGuard)
    with open(FILE_PIHOLE, 'w') as f:
        for entity in entities:
            domain = normalize_domain(entity)
            f.write(f"{domain}.com\n")
            f.write(f"www.{domain}.com\n")
    print(f"    > [SUBSTRATE: NETWORK] Generated {FILE_PIHOLE}")

    # 3. JSON PAYLOAD (Programmatic)
    json_data = [{"entity": e, "probable_domain": normalize_domain(e) + ".com"} for e in entities]
    with open(FILE_JSON, 'w') as f:
        json.dump(json_data, f, indent=4)
    print(f"    > [SUBSTRATE: CODE] Generated {FILE_JSON}")

    # 4. CSV MANIFEST (Human Analysis)
    with open(FILE_CSV, 'w') as f:
        f.write("Entity,Probable_Domain,Status\n")
        for entity in entities:
            f.write(f'"{entity}","{normalize_domain(entity)}.com","BLOCKED"\n')
    print(f"    > [SUBSTRATE: HUMAN] Generated {FILE_CSV}")

def main():
    print("/// ARKONIS PRIME: POLYMORPHIC DEFENSE PROTOCOL v3.0 ///")
    conn = setup_ledger()
    scan_the_grid_mock(conn)
    generate_artifacts(conn)
    conn.close()
    print("\n/// SYSTEM READY. DEPLOY ARTIFACTS IMMEDIATELY. ///")

if __name__ == "__main__":
    main()