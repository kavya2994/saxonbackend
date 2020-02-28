import os
import jwt
import time
import uuid
import random
import string
from datetime import datetime
from flask import current_app as app
from datetime import timedelta
from werkzeug.exceptions import Unauthorized
from werkzeug.exceptions import Unauthorized
from datetime import timedelta

from flask import make_response, request
from functools import update_wrapper
from . import APP

RESPONSE_OK = {"result": "Success"}


def delete_excel(filename):
    time.sleep(5)  # ??!!
    print("deleting file -" + filename)
    os.remove(filename)


def converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def token_verify_or_raise(token, user, ip):
    decoded_token = token_verify(token, user, ip)
    if decoded_token is None:
        raise Unauthorized()
    return decoded_token


def token_verify(token, user, ip):
    decoded = None

    try:
        decoded = jwt.decode(token, key=app.config['JWT_SECRET'])
        if decoded["username"] != user or decoded["Ipaddress"] != ip:
            decoded = None
        print(decoded)
    except jwt.DecodeError as e:
        print("decode error", e)

    except jwt.ExpiredSignatureError:
        print("sign")
    except KeyError:
        decoded = None
        print("key error")
    return decoded


def randomStringwithDigitsAndSymbols(stringLength=10):
    """Generate a random string of letters, digits and special characters """

    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))


def isDev():
    return "development" == os.getenv("BACKEND_ENV", default="")


def isProd():
    return "production" == os.getenv("BACKEND_ENV", default="")


def uuid_generator():
    return str(uuid.uuid4())
