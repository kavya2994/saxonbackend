import os


DEBUG = False
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

DBAAS_READONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@152.67.0.98:1521/?service_name=Dev_bom1sn.devpublic.dev.oraclevcn.com"
# DBAAS_WRITEONLY_CONNECTION_STRING = ""
