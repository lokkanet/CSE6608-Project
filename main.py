from flask import Flask, render_template, request, jsonify
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

# Initialize Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Load contract info
with open('deployment.json', 'r') as f:
    deployment = json.load(f)

contract = w3.eth.contract(
    address=deployment['contract_address'],
    abi=deployment['abi']
)

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')


@app.route('/')
def index():
    return render_template('index.html', contract_address=deployment['contract_address'])


@app.route('/get_value')
def get_value():
    try:
        value = contract.functions.get().call()
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/set_value', methods=['POST'])
def set_value():
    try:
        data = request.json
        new_value = int(data['value'])

        # Build transaction
        transaction = contract.functions.set(new_value).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'nonce': w3.eth.get_transaction_count(ACCOUNT_ADDRESS),
            'gas': 200000,
            'gasPrice': w3.to_wei('20', 'gwei'),
        })

        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            'success': True,
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt.blockNumber
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/get_owner')
def get_owner():
    try:
        owner = contract.functions.getOwner().call()
        return jsonify({'success': True, 'owner': owner})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
