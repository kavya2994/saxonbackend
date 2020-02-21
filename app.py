import os
from portal import create_app
from gevent.pywsgi import WSGIServer


if __name__ == "__main__":
    app = create_app()

    server_address = app.config['SERVER_ADDRESS']
    server_port = app.config['SERVER_PORT']

    print(f"Starting server on {server_address}:{server_port}")
    http_server = WSGIServer((server_address, server_port), app)

    http_server.serve_forever()
