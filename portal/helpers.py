import os
import jwt
import time
import random
import string
from flask_cors import CORS


def init_cors(app):
    CORS(app, resources={r"*": {"origins": "*"}})



def delete_excel(filename):
    time.sleep(5) #??!!
    print("deleting file" + filename)
    os.remove(filename)


def token_verify(token, user, ip):
    result = False
    try:
        decoded = jwt.decode(token, key='secret')
        if decoded["user"] == user and decoded["ip"] == ip:
            result = True
    except jwt.DecodeError:
        print("decode error")
        result = False
    except jwt.ExpiredSignatureError:
        print("sign")
        result = False
    except KeyError:
        print("key error")
    return result


def randomStringwithDigitsAndSymbols(stringLength=10):
    """Generate a random string of letters, digits and special characters """

    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))


def isDev():
    return "dev" == os.getenv("FLASK_ENV", default="")


def isProd():
    return "production" == os.getenv("FLASK_ENV", default="")
