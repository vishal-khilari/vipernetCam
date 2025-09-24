# src/pipeline.py

import os, sys
import json, time, csv
import joblib
from web3 import Web3
from dotenv import load_dotenv

# --- Add project root to path so src module can be found ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.encrypt_alert import encrypt_alert_bytes
from src.db import log_movement

# Load environment variables
load_dotenv()
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
RPC_URL = os.environ.get('RPC_URL', 'http://127.0.0.1:8545')
CHAIN_ID = int(os.environ.get('CHAIN_ID', 1337))

if not PRIVATE_KEY:
    raise SystemExit("PRIVATE_KEY not set in .env or environment")

# Load model & scaler
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'isolation_forest.joblib')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.joblib')
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Load contract info
BUILD_DIR = os.path.join(os.path.dirname(__file__), '..', 'build')
ABI = json.load(open(os.path.join(BUILD_DIR, 'EventLogger_abi.json')))
CONTRACT_ADDR = open(os.path.join(BUILD_DIR, 'EventLogger_addr.txt')).read().strip()

# Web3 connection
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise SystemExit(f"Cannot connect to RPC at {RPC_URL}")

acct = w3.eth.account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=CONTRACT_ADDR, abi=ABI)

# Optional IPFS
try:
    import ipfshttpclient
    ipfs_client = ipfshttpclient.connect()
except Exception:
    ipfs_client = None

def to_features(packet: dict):
    return [
        float(packet.get('speed_kmph', 0.0)),
        float(packet.get('turn_angle', 0.0)),
        float(packet.get('ang_vel', 0.0)),
        float(packet.get('hour_sin', 0.0)),
        float(packet.get('hour_cos', 0.0))
    ]

def handle_packet(packet: dict):
    X = scaler.transform([to_features(packet)])
    pred = model.predict(X)[0]
    score = float(model.decision_function(X)[0])
    packet['anomaly'] = 1 if pred == -1 else 0

    if packet['anomaly']:
        alert_json = json.dumps({
            "timestamp": packet.get('timestamp'),
            "zone": packet.get('entry_zone'),
            "lat": packet.get('latitude'),
            "lon": packet.get('longitude'),
            "speed": packet.get('speed_kmph'),
            "score": score
        }).encode('utf-8')

        encrypted = encrypt_alert_bytes(alert_json)
        packet['alert_token_hex'] = encrypted.hex()

        ipfs_cid = None
        if ipfs_client:
            try:
                ipfs_cid = ipfs_client.add_bytes(encrypted)
                packet['ipfs_cid'] = ipfs_cid
            except Exception as e:
                print("IPFS add failed:", e)
                ipfs_cid = None

        data_hash = w3.keccak(encrypted)
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = contract.functions.logEvent(data_hash, ipfs_cid or "", int(time.time())).build_transaction({
            'from': acct.address,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'chainId': CHAIN_ID
        })
        signed_tx = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        packet['tx_hash'] = receipt.transactionHash.hex()

    log_movement(packet)

FEATURES_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'features.csv')
with open(FEATURES_CSV, 'r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        handle_packet(row)
        time.sleep(0.05)
