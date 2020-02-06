import os
from portal import create_app
from gevent.pywsgi import WSGIServer


def get_config_file_path():
    env = os.getenv("FLASK_ENV", default="dev")
    base = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.abspath(os.path.join(base, 'config', env + '.py'))
    return absolute_path


if __name__ == "__main__":
    config = get_config_file_path()
    app = create_app(config)

    server_address = app.config['SERVER_ADDRESS']
    server_port = app.config['SERVER_PORT']

    print(f"starting server on {server_address}:{server_port}")
    http_server = WSGIServer((server_address, server_port), app)
    http_server.serve_forever()
