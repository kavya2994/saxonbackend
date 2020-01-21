import os
from portal import create_app


def get_config_file_path():
    env = os.getenv("FLASK_ENV", default="dev")
    absolute_path = os.path.abspath(os.path.join('config', f'{env}.py'))
    return absolute_path


if __name__ == "__main__":
    config=get_config_file_path()
    create_app(config)
