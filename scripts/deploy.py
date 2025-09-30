from web3 import Web3
from solcx import compile_source, install_solc
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Install and set solidity compiler
install_solc('0.8.0')


class ContractDeployer:
    def __init__(self, provider_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))

        # Check connection
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum node")

        print(f"Connected to Ethereum node. Chain ID: {self.w3.eth.chain_id}")

    def compile_contract(self, contract_path):
        """Compile Solidity contract"""
        with open(contract_path, 'r') as file:
            contract_source = file.read()

        # Compile contract
        compiled_sol = compile_source(contract_source)

        # Get contract interface
        contract_id, contract_interface = compiled_sol.popitem()

        return contract_interface

    def deploy_contract(self, contract_interface, account_address, private_key):
        """Deploy contract to blockchain"""

        # Get contract bytecode and ABI
        bytecode = contract_interface['bin']
        abi = contract_interface['abi']

        # Create contract instance
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        # Build transaction
        transaction = contract.constructor().build_transaction({
            'from': account_address,
            'nonce': self.w3.eth.get_transaction_count(account_address),
            'gas': 2000000,
            'gasPrice': self.w3.to_wei('20', 'gwei'),
        })

        # Sign transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Contract deployed at address: {tx_receipt.contractAddress}")

        # Save deployment info
        deployment_info = {
            'contract_address': tx_receipt.contractAddress,
            'abi': abi,
            'transaction_hash': tx_hash.hex()
        }

        with open('deployment.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)

        return tx_receipt.contractAddress, abi


def main():
    # Configuration
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')  # Add to .env file
    ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')  # Add to .env file

    if not PRIVATE_KEY or not ACCOUNT_ADDRESS:
        print("Please set PRIVATE_KEY and ACCOUNT_ADDRESS in .env file")
        return

    # Deploy contract
    deployer = ContractDeployer()
    contract_interface = deployer.compile_contract('contracts/SimpleStorage.sol')

    contract_address, abi = deployer.deploy_contract(
        contract_interface,
        ACCOUNT_ADDRESS,
        PRIVATE_KEY
    )

    print(f"Deployment successful!")
    print(f"Contract Address: {contract_address}")


if __name__ == "__main__":
    main()
