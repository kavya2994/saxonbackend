import os
import jwt
import time
import uuid
import random
import string
from werkzeug.exceptions import Unauthorized
from datetime import timedelta
from flask import make_response, request
from functools import update_wrapper
from . import APP


def delete_excel(filename):
    time.sleep(5) #??!!
    print("deleting file" + filename)
    os.remove(filename)


def token_verify_or_raise(token, user, ip):
    decoded_token = token_verify(token, user, ip)
    if decoded_token == None:
        raise Unauthorized()
    return decoded_token


def token_verify(token, user, ip):
    decoded = None

    try:
        decoded = jwt.decode(token, key=APP.config['JWT_SECRET'])
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


def cors(func):
    def inner(**kwargs):

        return func(**kwargs)
    return inner



def crossdomain(origin=None, methods=None, headers=None, expose_headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True, credentials=False, whitelist=[]):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if expose_headers is not None and not isinstance(expose_headers, str):
        expose_headers = ', '.join(x.upper() for x in expose_headers)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = APP.make_default_options_response()
        return options_resp.headers['allow']


    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = APP.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            if request.environ.get('HTTP_ORIGIN') in whitelist:
                origin = request.environ.get('HTTP_ORIGIN')
            else:
                origin = ''

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if credentials:
                h['Access-Control-Allow-Credentials'] = 'true'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            if expose_headers is not None:
                h['Access-Control-Expose-Headers'] = expose_headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
