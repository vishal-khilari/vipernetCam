# src/db.py
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'forensics.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS intrusion_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    zone TEXT,
    latitude REAL,
    longitude REAL,
    speed REAL,
    turn_angle REAL,
    ang_vel REAL,
    anomaly INTEGER,
    alert_token_hex TEXT,
    ipfs_cid TEXT,
    tx_hash TEXT
)
''')
conn.commit()

def log_movement(row: dict):
    cur.execute('''
    INSERT INTO intrusion_logs (timestamp, zone, latitude, longitude, speed, turn_angle, ang_vel, anomaly, alert_token_hex, ipfs_cid, tx_hash)
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        row.get('timestamp'),
        row.get('entry_zone'),
        float(row.get('latitude', 0)),
        float(row.get('longitude', 0)),
        float(row.get('speed_kmph', 0)),
        float(row.get('turn_angle', 0)),
        float(row.get('ang_vel', 0)),
        int(row.get('anomaly', 0)),
        row.get('alert_token_hex'),
        row.get('ipfs_cid'),
        row.get('tx_hash')
    ))
    conn.commit()
