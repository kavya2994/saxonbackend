import os
from .. import APP


def create_folders():
    folders = APP.config['DIRECTORIES']
    folder_list = folders.split(",")
    for folder in folder_list:
        path = os.path.join(APP.config["DATA_DIR"], folder)
        if not os.path.exists(path):
            os.mkdir(path=path, mode=777)

