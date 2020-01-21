import os
from portal import create_app


def get_config_file_path():
    env = os.getenv("FLASK_ENV", default="dev")
    base = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.abspath(os.path.join(base, 'config', env + '.py'))
    return absolute_path


if __name__ == "__main__":
    config=get_config_file_path()
    create_app(config)
