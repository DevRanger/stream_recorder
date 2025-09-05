#!/usr/bin/env python3
"""
Minimal Flask test to isolate the issue
"""

from flask import Flask, jsonify

def create_minimal_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Hello World"
    
    @app.route('/api/test')
    def test():
        return jsonify({"status": "ok", "message": "test endpoint working"})
    
    return app

if __name__ == "__main__":
    app = create_minimal_app()
    app.run(debug=True, host="0.0.0.0", port=8001)
