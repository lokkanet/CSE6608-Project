
from flask import Flask, request, jsonify, session
from flask_cors import CORS
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'blockchain_connected': w3.is_connected(),
        'ipfs_connected': ipfs_client is not None
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        file_count = contract.functions.fileCount().call()
        return jsonify({
            'total_files': file_count,
            'total_users': len(users_db)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

