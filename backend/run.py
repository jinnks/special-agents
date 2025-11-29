# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Run script for Special Agents with gevent support
"""
from gevent import monkey
monkey.patch_all()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run with gevent WSGI server for production-like async performance
    from gevent.pywsgi import WSGIServer

    host = '0.0.0.0'
    port = 5000

    print(f"Starting Special Agents marketplace on http://{host}:{port}")
    print("Using gevent for async I/O handling")
    print("Press Ctrl+C to stop")

    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()
