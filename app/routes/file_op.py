from flask import Flask, request, jsonify, session
# from flask_cors import CORS
from web3 import Web3
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
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, CreatePostForm, AddWalletForm, FileUploadForm
from app.models import User, Post, Wallet, File
from urllib.parse import urlsplit
from app.utils.ipfs_op import ipfs_upload
from io import BytesIO


@app.route('/file/upload', methods=["GET", 'POST'])
@login_required
def upload_file():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        print(file.read(), form.file.data.filename)
        byte_file = file.read()

        file_hash = ipfs_upload(current_user.id, byte_file, current_user.wallet.address)

        stored_file_key = File(
            file_key=file_hash,
            file_name=f"{form.file.data.filename}"
        )
        db.session.add(stored_file_key)
        db.session.commit()
        print(current_user.files)
        current_user.files.append(stored_file_key)
        db.session.add(current_user)
        db.session.commit()

        flash('Congratulations')
        return redirect(url_for('index'))
    return render_template('file_upload.html', title='File Upload', form=form)




@app.route('/api/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """Download file from IPFS"""
    token = request.headers.get('Authorization')
    if not token or token not in sessions_db:
        return jsonify({'error': 'Unauthorized'}), 401

    username = sessions_db[token]['username']
    user = users_db[username]

    try:
        # Get file metadata from blockchain
        metadata = contract.functions.getFileMetadata(file_id).call({
            'from': user['eth_address']
        })

        ipfs_hash = metadata[3]
        is_encrypted = metadata[6]

        # Retrieve from IPFS
        if ipfs_client:
            file_content = ipfs_client.cat(ipfs_hash)
        else:
            return jsonify({'error': 'IPFS not available'}), 503

        # Decrypt if encrypted
        if is_encrypted:
            file_content = decrypt_data(
                file_content.decode(),
                user['private_key']
            ).encode('latin-1')

        return jsonify({
            'file_name': metadata[0],
            'file_type': metadata[1],
            'file_size': metadata[2],
            'content': file_content.decode('latin-1'),
            'ipfs_hash': ipfs_hash
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
def get_user_files():
    """Get all files owned by user"""
    token = request.headers.get('Authorization')
    if not token or token not in sessions_db:
        return jsonify({'error': 'Unauthorized'}), 401

    username = sessions_db[token]['username']
    user = users_db[username]

    try:
        file_ids = contract.functions.getUserFiles(user['eth_address']).call()

        files = []
        for file_id in file_ids:
            try:
                metadata = contract.functions.getFileMetadata(file_id).call({
                    'from': user['eth_address']
                })
                files.append({
                    'file_id': file_id,
                    'file_name': metadata[0],
                    'file_type': metadata[1],
                    'file_size': metadata[2],
                    'ipfs_hash': metadata[3],
                    'timestamp': metadata[5],
                    'is_encrypted': metadata[6]
                })
            except:
                continue

        return jsonify({'files': files}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/share', methods=['POST'])
def share_file():
    """Grant access to another user"""
    token = request.headers.get('Authorization')
    if not token or token not in sessions_db:
        return jsonify({'error': 'Unauthorized'}), 401

    username = sessions_db[token]['username']
    user = users_db[username]

    data = request.json
    file_id = data.get('file_id')
    recipient_address = data.get('recipient_address')
    can_share = data.get('can_share', False)

    try:
        tx_hash = contract.functions.grantAccess(
            file_id,
            recipient_address,
            can_share
        ).transact({'from': user['eth_address']})

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            'message': 'Access granted successfully',
            'tx_hash': receipt.transactionHash.hex()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/revoke', methods=['POST'])
def revoke_access():
    """Revoke access from a user"""
    token = request.headers.get('Authorization')
    if not token or token not in sessions_db:
        return jsonify({'error': 'Unauthorized'}), 401

    username = sessions_db[token]['username']
    user = users_db[username]

    data = request.json
    file_id = data.get('file_id')
    recipient_address = data.get('recipient_address')

    try:
        tx_hash = contract.functions.revokeAccess(
            file_id,
            recipient_address
        ).transact({'from': user['eth_address']})

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            'message': 'Access revoked successfully',
            'tx_hash': receipt.transactionHash.hex()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
