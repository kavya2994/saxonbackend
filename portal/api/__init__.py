from flask import Blueprint
from flask_restplus import Api


api = Api(version='1.0', title='Saxon Pensions API', doc='/doc/')

def init_app(app):
    api_v1 = Blueprint('api', __name__, url_prefix='/api/v1', template_folder='templates')
    api.init_app(api_v1)
    app.register_blueprint(api_v1)
