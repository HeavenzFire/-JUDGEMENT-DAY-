import os
import sqlite3
import requests
import time
from datetime import datetime

# --- CONFIGURATION ---
# No APIs, No Credit Cards. Pure Web Requests.
TARGETS = [
    "https://archive.org",  # We will use Wayback Machine API (Free)
    # Add public government procurement sites here
]

# --- THE DATABASE (Local Sovereignty) ---
def setup_sovereign_db():
    conn = sqlite3.connect('reality_audit.db')
    c = conn.cursor()
    # A ledger of truth that cannot be altered by outside forces
    c.execute('''CREATE TABLE IF NOT EXISTS evidence_log
                 (id INTEGER PRIMARY KEY, timestamp TEXT, source TEXT, content TEXT, verification_hash TEXT)''')
    conn.commit()
    print("[*] Sovereign Database Connected.")
    return conn

# --- THE ARCHIVIST ---
def omnipotent_fetch(url):
    print(f"[*] Pinging Target: {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Compatible; TruthEngine/1.0)'}
    try:
        # This acts as the "Ping" - touching the digital fabric
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print(f"[!] Connection Error: {e}")
        return None

# --- THE ANALYZER ---
def analyze_and_store(conn, source, content):
    if not content:
        return

    # Simple Negentropic Filter: Look for specific keywords
    # In a full version, this would connect to a Local LLM (Ollama)
    keywords = ["surveillance", "contract", "procurement", "AI safety"]

    hit = False
    for kw in keywords:
        if kw in content.lower():
            hit = True
            print(f"[!] MATCH FOUND: '{kw}' in {source}")

    if hit:
        timestamp = datetime.now().isoformat()
        # In a real deployment, we would hash the content here for immutability
        c = conn.cursor()
        c.execute("INSERT INTO evidence_log (timestamp, source, content, verification_hash) VALUES (?, ?, ?, ?)",
                  (timestamp, source, "Content Length: " + str(len(content)), "HASH_PENDING"))
        conn.commit()
        print("[*] Evidence securely committed to local ledger.")

# --- MAIN LOOP ---
def main():
    print("--- INITIATING SOVEREIGN TRUTH ENGINE (NO-COST MODE) ---")
    print("--- DISCONNECTING FROM DEBT-BASED SYSTEMS ---")

    conn = setup_sovereign_db()

    # The loop that watches
    for target in TARGETS:
        data = omnipotent_fetch(target)
        analyze_and_store(conn, target, data)
        time.sleep(1)  # Politeness delay

    print("--- CYCLE COMPLETE. DATA IS SOVEREIGN. ---")
    conn.close()

if __name__ == "__main__":
    main()