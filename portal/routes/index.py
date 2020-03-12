from flask import request, render_template, Response
from flask_restx import Resource
from ..api import api
from .. import APP, LOG


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
        x_real_ip = request.headers['X-Real-Ip'] if 'X-Real-Ip' in request.headers else None
        LOG.info('X-Real-Ip: %s', x_real_ip)

        x_forwarded_ip = request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else None
        LOG.info('X-Forwarded-For: %s', x_forwarded_ip)

        flask_remote_addr = request.environ['REMOTE_ADDR'] if 'REMOTE_ADDR' in request.environ else ''
        LOG.info('REMOTE_ADDR: %s', flask_remote_addr)

        user_ip = x_real_ip if x_real_ip else x_forwarded_ip if x_forwarded_ip else flask_remote_addr
        return { 'ip': user_ip }
