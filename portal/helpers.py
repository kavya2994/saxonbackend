import os
import jwt
import time
import random
import string
from flask_cors import CORS


def init_cors(app):
    CORS(app, resources={"/login1": {
    "origins": ['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
                'http://192.168.2.146:812']},
                     "/checktoken": {"origins": ['https://angularproject-5c26e.firebaseapp.com',
                                                 'http://localhost:4200', 'http://183.82.0.186:812',
                                                 'http://192.168.2.146:812']},
                     "/initiate_enrollment": {"origins": ['https://angularproject-5c26e.firebaseapp.com',
                                                          'http://localhost:4200', 'http://183.82.0.186:812',
                                                          'http://192.168.2.146:812']},
                     "/enrollment": {"origins": ['https://angularproject-5c26e.firebaseapp.com',
                                                 'http://localhost:4200', 'http://183.82.0.186:812',
                                                 'http://192.168.2.146:812']}
                     })


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
