#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-Talk Digital Coupon Demo Server
"""

from flask import Flask, send_file, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve dashboard"""
    return send_file('demo_dashboard.html')

@app.route('/config/keys_public.json')
def keys_public():
    """Serve public keys"""
    try:
        with open('config/keys_public.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Keys not found"}), 404

@app.route('/api/test-results')
def test_results():
    """Get test results"""
    return jsonify({
        "key_management": "pass",
        "reward_calculator": "pass",
        "reserve_manager": "pass",
        "invariants": "pending",
        "asa_creation": "pending"
    })

if __name__ == "__main__":
    print("=" * 60)
    print("PAM-Talk Digital Coupon - Demo Dashboard")
    print("=" * 60)
    print("\nOpen in browser: http://localhost:8000")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=8000)
