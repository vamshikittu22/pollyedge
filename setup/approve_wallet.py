#!/usr/bin/env python3
"""
PollyEdge Wallet Setup — Run ONCE before any bot trading.
Approves Polymarket to use your USDC. Never needs repeating.

Usage: python setup/approve_wallet.py
"""
import os
import sys

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = "https://polygon-rpc.com"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FUNDER = os.getenv("FUNDER")

if not PRIVATE_KEY or not FUNDER:
    print("ERROR: Set PRIVATE_KEY and FUNDER in your .env file first.")
    sys.exit(1)

# Polymarket contract addresses (Polygon mainnet)
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC.e
CTF_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
EXCHANGE_ADDR = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

MAX_UINT = 2**256 - 1

# ERC20 approve ABI (minimal)
ERC20_ABI = [
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    }
]

usdc = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)


def approve(spender: str, label: str) -> None:
    """Send an ERC20 approval transaction."""
    tx = usdc.functions.approve(spender, MAX_UINT).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 100000,
            "gasPrice": w3.to_wei("30", "gwei"),
        }
    )
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    txhash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Approved {label}: {txhash.hex()}")
    w3.eth.wait_for_transaction_receipt(txhash)


if __name__ == "__main__":
    print("PollyEdge Wallet Approval")
    print(f"Wallet: {account.address}")
    print(f"Network: Polygon Mainnet (Chain ID 137)")
    print()

    approve(CTF_ADDRESS, "CTF Contract")
    approve(EXCHANGE_ADDR, "CLOB Exchange")

    print()
    print("All approvals done. Never need to run this again.")
