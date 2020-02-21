import os
from .base import *


DEBUG = True

DATA_DIR = "/var/www/data/"
ZIP_DATA_DIR = "/var/www/backend/ZIP/"

DBAAS_READONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@152.67.0.98:1521/?service_name=Dev_bom1sn.devpublic.dev.oraclevcn.com"
DBAAS_WRITEONLY_CONNECTION_STRING = "oracle+cx_oracle://system:Sportal_DB#23@140.238.248.176:1521/?service_name=PDB1.svcsubnetad1.svcvcn.oraclevcn.com"

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 90
SERVER_WEB_URL = 'https://portal.silverthatch.org.ky/'

SECRET_KEY = 'f^I7q!(S(O]|"]%<+,Hz&vyQ^"exx9'
JWT_SECRET = 'H7|=1fq[:`.;MtY02Me]w9_XPRqt^S'

CORS_ORIGIN_WHITELIST = [
    "http://generator.swagger.io",
    "https://generator.swagger.io",

    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://127.0.0.1:5000",
    "https://127.0.0.1:5000",
    "http://127.0.0.1:4200",
    "https://127.0.0.1:4200",

    "http://localhost",
    "https://localhost",
    "http://localhost:5000",
    "https://localhost:5000",
    "http://localhost:4200",
    "https://localhost:4200",

    "http://10.147.1.101",
    "https://10.147.1.101",

    "http://10.147.1.101:4200",
    "https://10.147.1.101:4200",

    "http://132.145.107.163",
    "https://132.145.107.163",
    "http://192.168.2.146:8080",
    "http://192.168.2.146:812",
    "http://192.168.2.132:812",

    "http://portal.silverthatch.org.ky",
    "https://portal.silverthatch.org.ky"
]
