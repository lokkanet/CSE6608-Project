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



def ipfs_upload(user, file, public_key):
    encrypted_file = encrypt_data(file, public_key)
    print("enc", encrypted_file)

    file_path = f"app/userfiles/text{user}.txt"
    with open(file_path, "w") as f:
        f.write(f"{encrypted_file}")

    file_hash = ""
    with ipfshttpclient.connect() as client:
        file_hash = client.add(file_path)['Hash']
        print(client, file_hash)

    os.remove(file_path)

    return file_hash

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
