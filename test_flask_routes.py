#!/usr/bin/env python3
"""
Simple Flask test to check if the concatenation route is registered
"""

from flask import Flask, jsonify

def create_test_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Flask Test App Running"
    
    @app.route('/api/concatenate', methods=['POST'])
    def test_concatenate():
        return jsonify({
            'status': 'test_success',
            'message': 'Concatenation endpoint is reachable',
            'method': 'POST'
        })
    
    @app.route('/api/concatenate', methods=['GET'])
    def test_concatenate_get():
        return jsonify({
            'status': 'test_success',
            'message': 'Concatenation endpoint is reachable',
            'method': 'GET'
        })
    
    # List all routes
    @app.route('/api/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return jsonify({'routes': routes})
    
    return app

if __name__ == "__main__":
    app = create_test_app()
    print("Starting test Flask app...")
    print("Routes available:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {list(rule.methods)} {rule}")
    print()
    app.run(debug=True, host="0.0.0.0", port=8002)
