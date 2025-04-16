#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application runner for the novel generator.
This is the entry point for running the Flask application.
"""

import os
from app import create_app

try:
    # 新しい方式を試す
    app = create_app()
except ImportError:
    # 失敗した場合は従来の方式
    print("Using legacy app structure...")
    from app import app

if __name__ == '__main__':
    print("Starting Novel Generator Flask application...")
    
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port)