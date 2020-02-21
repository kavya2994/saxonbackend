import os
from .. import APP


def create_folders():
    for folder in APP.config['DIRECTORIES']:
        path = os.path.join(APP.config["DATA_DIR"], folder)
        if not os.path.exists(path):
            os.mkdir(path=path, mode=777)

