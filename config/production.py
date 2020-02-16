import os


DATA_DIR = "/var/www/data"
DEBUG = False

DBAAS_READONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@152.67.0.98:1521/?service_name=Dev_bom1sn.devpublic.dev.oraclevcn.com"
DBAAS_WRITEONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@140.238.248.176:1521/?service_name=PDB1.svcsubnetad1.svcvcn.oraclevcn.com"

SERVER_WEB_URL = 'https://portal.silverthatch.org.ky/'
SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 811

CERT_KEY_FILE = "/var/www/certs/privkey.pem"
CERT_FILE = "/var/www/certs/fullchain.pem"

SECRET_KEY = 'f^I7q!(S(O]|"]%<+,Hz&vyQ^"exx9'
JWT_SECRET = 'H7|=1fq[:`.;MtY02Me]w9_XPRqt^S'

MAILGUN_API_KEY = "1dcbf1bdff3416543d67867101b08e49-52b6835e-5b18bf8e"
MAILGUN_DOMAIN = "sandbox6edce741885a45088acf63216cdf5660.mailgun.org"
