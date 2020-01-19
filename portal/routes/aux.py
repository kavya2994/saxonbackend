from flask import Blueprint, jsonify, request

aux_blueprint = Blueprint('aux_blueprint', __name__, template_folder='templates')


@aux_blueprint.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    print(request.headers)
    return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
