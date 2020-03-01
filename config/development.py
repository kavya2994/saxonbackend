import logging


LOG_LEVEL = logging.DEBUG

DATA_DIR = "E:/Saxons_folders/"
LOG_DIR = "C:/Users/Manomay/Desktop/backend-0/"
ZIP_DATA_DIR = "C:/Users/Manomay/Desktop/backend-0/data/zip/"
EXCEL_TEMPLATE_DIR = "C:/Users/Manomay/Desktop/backend-0/data/excel/"

DIRECTORIES = [
    'termination', 'Statements', 'rev_inbox', 'Resources', 'pensioninfo',
    'Monthly', 'member_resources', 'enrollment', 'Employers', 'emp_inbox',
    'contribution', 'batch', 'Annual',
]

DBAAS_READONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@152.67.0.98:1521/?service_name=Dev_bom1sn.devpublic.dev.oraclevcn.com"
DBAAS_WRITEONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@140.238.248.176:1521/?service_name=PDB1.svcsubnetad1.svcvcn.oraclevcn.com"

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 811
SERVER_WEB_URL = f'http://{SERVER_ADDRESS}:{SERVER_PORT}/static/'

FRONTEND_URL = 'http://192.168.2.132:812/'

SECRET_KEY = 'BT-=f~i1IlIHF(#'
JWT_SECRET = 'R]B+=46,e=gKtI/'

CORS_HEADERS = [
    'Ipaddress', 'Authorization', 'username',
    'Content-Type'
]

CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://127.0.0.1:5000",
    "https://127.0.0.1:5000",
    "http://127.0.0.1:4200",
    "https://127.0.0.1:4200",
    "http://192.168.2.146:8080",
    "http://192.168.2.146:812",
    "http://localhost",
    "https://localhost",
    "http://localhost:5000",
    "https://localhost:5000",
    "http://localhost:4200",
    "https://localhost:4200",
    "http://192.168.2.132:812"
]

MAILGUN_API_KEY = "1dcbf1bdff3416543d67867101b08e49-52b6835e-5b18bf8e"
MAILGUN_DOMAIN = "sandbox6edce741885a45088acf63216cdf5660.mailgun.org"

MAILDOMAIN = "smtp.gmail.com"
MAILPORT = 465
EMAIL = "portals.uat@gmail.com"
PASSWORD = "Portal@Success"
