# src/deploy_contract.py
import os, json, sys
from web3 import Web3
from solcx import compile_standard, install_solc, set_solc_version
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure solc compiler is installed and selected
try:
    install_solc("0.8.17")
    set_solc_version("0.8.17")
except Exception as e:
    print("❌ Error installing or setting solc version:", e)
    sys.exit(1)

# Read env variables
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
RPC_URL = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
CHAIN_ID = int(os.environ.get("CHAIN_ID", 1337))

if not PRIVATE_KEY:
    print("❌ ERROR: PRIVATE_KEY not set in environment (.env or export).")
    sys.exit(1)

if not PRIVATE_KEY.startswith("0x"):
    PRIVATE_KEY = "0x" + PRIVATE_KEY

# Path to contract
CONTRACT_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "EventLogger.sol")
CONTRACT_PATH = os.path.normpath(CONTRACT_PATH)

if not os.path.exists(CONTRACT_PATH):
    print(f"❌ ERROR: Contract file not found at {CONTRACT_PATH}")
    sys.exit(1)

# Read contract source
with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
    source = f.read()

print("🔨 Compiling Solidity contract...")
compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"EventLogger.sol": {"content": source}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
    }
)

contract_data = compiled["contracts"]["EventLogger.sol"]["EventLogger"]
bytecode = contract_data["evm"]["bytecode"]["object"]
abi = contract_data["abi"]

# Connect to blockchain
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("❌ ERROR: Could not connect to RPC at", RPC_URL)
    sys.exit(1)

# Load account from private key
acct = w3.eth.account.from_key(PRIVATE_KEY)
print("📌 Deploying from account:", acct.address)

# Build contract
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(acct.address)

transaction = contract.constructor().build_transaction(
    {
        "from": acct.address,
        "nonce": nonce,
        "gas": 4000000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "chainId": CHAIN_ID,
    }
)

# Sign & send
signed_txn = acct.sign_transaction(transaction)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

print("🚀 Transaction sent. Tx hash:", tx_hash.hex())

print("⏳ Waiting for receipt...")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

print("✅ Contract deployed at address:", receipt.contractAddress)

# Save ABI & contract address
build_dir = os.path.join(os.path.dirname(__file__), "..", "build")
os.makedirs(build_dir, exist_ok=True)

with open(os.path.join(build_dir, "EventLogger_abi.json"), "w") as f:
    json.dump(abi, f)

with open(os.path.join(build_dir, "EventLogger_addr.txt"), "w") as f:
    f.write(receipt.contractAddress)

print("📂 ABI and contract address saved to build/ directory.")
