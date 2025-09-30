from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

print("=" * 50)
print("GANACHE ACCOUNT CHECKER")
print("=" * 50)

# Check connection
if w3.is_connected():
    print("✓ Connected to Ganache")
    print(f"Chain ID: {w3.eth.chain_id}")
else:
    print("✗ Failed to connect to Ganache")
    print("Make sure ganache-cli is running!")
    exit(1)

# Get all accounts from Ganache
accounts = w3.eth.accounts
print(f"\nFound {len(accounts)} accounts in Ganache:\n")

for i, account in enumerate(accounts):
    balance = w3.eth.get_balance(account)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"Account {i}: {account}")
    print(f"Balance: {balance_eth} ETH\n")

# Check your configured account
print("=" * 50)
print("YOUR CONFIGURED ACCOUNT")
print("=" * 50)

account_address = os.getenv('ACCOUNT_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

if account_address and private_key:
    print(f"Address: {account_address}")

    # Check if it's a valid address
    if w3.is_address(account_address):
        balance = w3.eth.get_balance(account_address)
        balance_eth = w3.from_wei(balance, 'ether')

        if balance > 0:
            print(f"Balance: {balance_eth} ETH ✓")
            print("You have funds! Ready to deploy.")
        else:
            print(f"Balance: {balance_eth} ETH ✗")
            print("\nPROBLEM: Your account has no funds!")
            print("\nSOLUTION:")
            print("1. Copy one of the accounts above")
            print("2. Update your .env file with:")
            print(f"   ACCOUNT_ADDRESS={accounts[0]}")
            print("   PRIVATE_KEY=<get from ganache-cli output>")
    else:
        print("✗ Invalid address format!")
else:
    print("✗ No account configured in .env file!")
    print("\nAdd these to your .env file:")
    print(f"ACCOUNT_ADDRESS={accounts[0]}")
    print("PRIVATE_KEY=<get from ganache-cli startup message>")

print("\n" + "=" * 50)
print("TIPS")
print("=" * 50)
print("• Ganache creates 10 accounts with 100 ETH each")
print("• Use any of these accounts for testing")
print("• Private keys are shown when ganache-cli starts")
print("• NEVER use these keys on real networks!")