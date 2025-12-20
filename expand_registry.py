import hashlib
import sqlite3
import random
import string

def generate_new_artifacts(count=10):
    artifacts = []
    for i in range(count):
        name = f"Syntropic Artifact {i+1}: {''.join(random.choices(string.ascii_letters, k=10))}"
        logic_hash = hashlib.sha256(name.encode()).hexdigest()
        artifact = {
            'id': f"ART-{i+1}",
            'name': name,
            'logic_hash': logic_hash
        }
        artifacts.append(artifact)
    return artifacts

def expand_registry(nonprofit, db_path='heavenzfire.db'):
    new_artifacts = generate_new_artifacts()
    gift_registry = nonprofit.manifest_gift_portal(new_artifacts)
    
    # Log to DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS gift_ledger (
                        id TEXT PRIMARY KEY,
                        content TEXT,
                        license TEXT,
                        verification TEXT,
                        delivery_mode TEXT,
                        timestamp TEXT
                      )''')
    import datetime
    for gift in gift_registry:
        cursor.execute('INSERT INTO gift_ledger VALUES (?, ?, ?, ?, ?, ?)',
                       (gift['id'], gift['content'], gift['license'], gift['verification'], gift['delivery_mode'], datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    print(f"[EXPAND] Registry expanded with {len(gift_registry)} new gifts.")
    return gift_registry