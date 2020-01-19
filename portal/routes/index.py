from flask import Blueprint, render_template

index_blueprint = Blueprint('index_blueprint', __name__, template_folder='templates')

@index_blueprint.route('/')
def index():
    try:
        return render_template('pages/index.html')
    except:
        return "Not Found", 404

