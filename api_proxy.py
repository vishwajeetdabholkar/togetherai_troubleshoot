#!/usr/bin/env python3
"""
Simple API proxy to handle Together AI requests and avoid CORS issues
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return send_from_directory('.', 'ui.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    """Proxy for Together AI models endpoint"""
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 401
    
    try:
        response = requests.get(
            'https://api.together.xyz/v1/models',
            headers={'Authorization': api_key},
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': f'API request failed with status {response.status_code}',
                'status_code': response.status_code,
                'response': response.text[:500]
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error'}), 503
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/inference', methods=['POST'])
def inference():
    """Proxy for Together AI inference endpoint"""
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 401
    
    try:
        payload = request.get_json()
        response = requests.post(
            'https://api.together.xyz/inference',
            headers={'Authorization': api_key, 'Content-Type': 'application/json'},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': f'Inference request failed with status {response.status_code}',
                'status_code': response.status_code,
                'response': response.text[:500]
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error'}), 503
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Together AI Troubleshooting Tool API Proxy...")
    print("Access the UI at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
