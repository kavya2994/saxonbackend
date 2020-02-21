from flask import Blueprint
from flask_restplus import Api
from werkzeug.exceptions import HTTPException


api = Api(version='1.0', title='Saxon Pensions API', doc='/doc/', catch_all_404s=True)

def init_app(app):
    v1 = Blueprint('api', __name__, url_prefix='/v1', template_folder='templates')
    api.init_app(v1)
    app.register_blueprint(v1)

    @api.errorhandler(HTTPException)
    def handle_http_exception_with_cors(error):
        return {'message': str(error)}, getattr(error, 'code', 500), {'Access-Control-Allow-Origin': '*'}

    app.logger.info('Initialized api')
