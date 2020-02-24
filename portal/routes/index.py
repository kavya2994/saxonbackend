from flask import request, render_template, Response
from flask_restplus import Resource
from ..api import api


@api.route('/index')
class Index(Resource):
    @api.doc('get_index', responses={404: "Not Found", 200: "OK"})
    def get(self):
        try:
            data = render_template('pages/index.html')
            response = Response(data, mimetype='text/html')
            response.status_code = 200
            return response
        except:
            return "Not Found", 404


# PLEASE DO NOT REMOVE THIS
@api.route('/ip')
@api.doc(description='Get user\'s IP address')
class MyIP(Resource):
    def get(self):
        return { 'ip': request.environ['REMOTE_ADDR'] }
