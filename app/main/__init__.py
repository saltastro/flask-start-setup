from bokeh.resources import CDN
from flask import Blueprint

main = Blueprint('main', __name__)


@main.context_processor
def bokeh_resources():
    return dict(bokeh_resources=CDN)


from . import views, errors
