import os
import jwt
import time
import uuid
import random
import string
from flask import current_app as app
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized


def init_cors(app):
    CORS(app, resources={r"*": {"origins": "*"}})


def delete_excel(filename):
    time.sleep(5)  # ??!!
    print("deleting file" + filename)
    os.remove(filename)


def token_verify_or_raise(token, user, ip):
    decoded_token = token_verify(token, user, ip)
    if decoded_token is None:
        raise Unauthorized()
    return decoded_token


def token_verify(token, user, ip):
    decoded = None

    try:
        decoded = jwt.decode(token, key=app.config['JWT_SECRET'])
        if decoded["Username"] != user or decoded["IpAddress"] != ip:
            decoded = None

    except jwt.DecodeError:
        print("decode error")
    except jwt.ExpiredSignatureError:
        print("sign")
    except KeyError:
        print("key error")
    return decoded


def randomStringwithDigitsAndSymbols(stringLength=10):
    """Generate a random string of letters, digits and special characters """

    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))


def isDev():
    return "development" == os.getenv("FLASK_ENV", default="")


def isProd():
    return "production" == os.getenv("FLASK_ENV", default="")


def uuid_generator():
    return str(uuid.uuid4())
