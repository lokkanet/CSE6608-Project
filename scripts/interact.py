from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()


class ContractInteractor:
    def __init__(self, provider_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))

        # Load deployment info
        with open('deployment.json', 'r') as f:
            deployment = json.load(f)

        self.contract_address = deployment['contract_address']
        self.abi = deployment['abi']

        # Create contract instance
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

    def get_stored_value(self):
        """Get the stored value from contract"""
        try:
            value = self.contract.functions.get().call()
            return value
        except Exception as e:
            print(f"Error getting value: {e}")
            return None

    def set_value(self, value, account_address, private_key):
        """Set a new value in the contract"""
        try:
            # Build transaction
            transaction = self.contract.functions.set(value).build_transaction({
                'from': account_address,
                'nonce': self.w3.eth.get_transaction_count(account_address),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
            })

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            print(f"Transaction successful! Hash: {tx_hash.hex()}")
            return tx_receipt

        except Exception as e:
            print(f"Error setting value: {e}")
            return None

    def get_owner(self):
        """Get contract owner"""
        return self.contract.functions.getOwner().call()

    def listen_for_events(self):
        """Listen for DataStored events"""
        event_filter = self.contract.events.DataStored.create_filter(fromBlock='latest')

        print("Listening for events... Press Ctrl+C to stop")
        try:
            while True:
                for event in event_filter.get_new_entries():
                    print(f"New event: Data {event['args']['data']} stored by {event['args']['user']}")
        except KeyboardInterrupt:
            print("Stopped listening for events")


def main():
    # Configuration
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')

    interactor = ContractInteractor()

    while True:
        print("\n=== Smart Contract Interaction ===")
        print("1. Get stored value")
        print("2. Set new value")
        print("3. Get owner")
        print("4. Listen for events")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            value = interactor.get_stored_value()
            print(f"Stored value: {value}")

        elif choice == '2':
            try:
                new_value = int(input("Enter new value: "))
                result = interactor.set_value(new_value, ACCOUNT_ADDRESS, PRIVATE_KEY)
                if result:
                    print("Value set successfully!")
            except ValueError:
                print("Please enter a valid number")

        elif choice == '3':
            owner = interactor.get_owner()
            print(f"Contract owner: {owner}")

        elif choice == '4':
            interactor.listen_for_events()

        elif choice == '5':
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()