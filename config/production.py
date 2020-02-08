import os


DEBUG = False
DATA_DIR = "/var/www/data" #os.path.join(os.path.dirname(__file__), '..', '..', 'data')

CERT_KEY_FILE = "/var/www/certs/privkey.pem"
CERT_FILE = "/var/www/certs/fullchain.pem"

DBAAS_READONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@152.67.0.98:1521/?service_name=Dev_bom1sn.devpublic.dev.oraclevcn.com"
DBAAS_WRITEONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@140.238.248.176:1521/?service_name=PDB1.svcsubnetad1.svcvcn.oraclevcn.com"

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 443
