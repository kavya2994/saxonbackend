import os


DATA_DIR = "/var/www/data"
DEBUG = False

DBAAS_READONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@152.67.0.98:1521/?service_name=Dev_bom1sn.devpublic.dev.oraclevcn.com"
DBAAS_WRITEONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@140.238.248.176:1521/?service_name=PDB1.svcsubnetad1.svcvcn.oraclevcn.com"

SERVER_WEB_URL = 'https://portal.silverthatch.org.ky/'
SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 443

CERT_KEY_FILE = "/var/www/certs/privkey.pem"
CERT_FILE = "/var/www/certs/fullchain.pem"

SECRET_KEY = 'f^I7q!(S(O]|"]%<+,Hz&vyQ^"exx9'
JWT_SECRET = 'H7|=1fq[:`.;MtY02Me]w9_XPRqt^S'

MAILGUN_API_KEY = "1dcbf1bdff3416543d67867101b08e49-52b6835e-5b18bf8e"
MAILGUN_DOMAIN = "sandbox6edce741885a45088acf63216cdf5660.mailgun.org"

CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1/",
    "https://127.0.0.1/",
    "http://127.0.0.1:5000/",
    "https://127.0.0.1:5000/",
    "http://127.0.0.1:4200/",
    "https://127.0.0.1:4200/",

    "http://localhost/",
    "https://localhost/",
    "http://localhost:5000/",
    "https://localhost:5000/",
    "http://localhost:4200/",
    "https://localhost:4200/",

    "http://10.147.1.101/",
    "https://10.147.1.101/",

    "http://10.147.1.101:4200/",
    "https://10.147.1.101:4200/",
    "http://portal.silverthatch.org.ky/"
    "https://portal.silverthatch.org.ky/"
]
