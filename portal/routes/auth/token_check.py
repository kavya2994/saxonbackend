import jwt
import json
from flask import request
from flask_restplus import Resource, reqparse
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('User', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

@ns.route('/token/check')
class TokenCheck(Resource):
    @ns.doc(parser=parser,
        description='Validates the user token',
        responses={400: 'Bad Request', 401: 'Unauthorized', 200: 'OK'})

    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        result = False
        print(request.headers)

        try:
            token = args["Authorization"]
            print(request.get_data())
            data = json.loads(str(request.data, encoding='utf-8'))
            decoded = jwt.decode(token, key='secret')
            print(decoded["User"])
            if decoded["User"] == args["User"] and decoded["IP"] == args["IpAddress"]:
                result = True
        except jwt.DecodeError:
            print("decode error")
            result = False
        except jwt.ExpiredSignatureError:
            print("sign")
            result = False
        except KeyError:
            print("key error")
            print(result)

        return {"result": result}, 200 if result else 401
