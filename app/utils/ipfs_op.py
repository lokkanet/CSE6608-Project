import ipfshttpclient
import json
import os
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import hashlib
import secrets
import os
from .encryptions import encrypt_data


def ipfs_upload(file, public_key):
    encrypted_file = encrypt_data(file, public_key)

    with ipfshttpclient.connect() as client:
        hash = client.add('test.txt')['Hash']
        print(client.stat(hash))



    # # Register on blockchain
    # tx_hash = contract.functions.uploadFile(
    #     file.filename,
    #     file.content_type or 'application/octet-stream',
    #     len(file_content),
    #     ipfs_hash,
    #     encrypt
    # ).transact({'from': user['eth_address']})
    #
    # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    #
    # # Extract file ID from event logs
    # file_id = contract.events.FileUploaded().process_receipt(receipt)[0]['args']['fileId']

    # return jsonify({
    #     'message': 'File uploaded successfully',
    #     'file_id': file_id,
    #     'ipfs_hash': ipfs_hash,
    #     'tx_hash': receipt.transactionHash.hex()
    # }), 201
