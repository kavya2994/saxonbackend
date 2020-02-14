DATA_DIR = "./data"
DEBUG = True

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 5000
SERVER_WEB_URL = f'http://{SERVER_ADDRESS}:{SERVER_PORT}/static/'

SECRET_KEY = 'BT-=f~i1IlIHF(#'
JWT_SECRET = 'R]B+=46,e=gKtI/'

CERT_KEY_FILE = ""
CERT_FILE = ""

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
]
