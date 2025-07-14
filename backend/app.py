import logging

from flask import Flask, render_template

from area.routes import area_blueprint, get_available_areas, get_area_metadata
from quiz.routes import quiz_blueprint

__version__ = '0.1.0'
app = Flask(__name__)
app.secret_key = 'mega-secret-housetour'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app.logger.setLevel(logging.INFO)

app.register_blueprint(area_blueprint)
app.register_blueprint(quiz_blueprint)


@app.route('/')
def index():
    area_list = [
        {
            'url': f'/area/{area}',
            'name': get_area_metadata(area).get('title', area),
        }
        for area in get_available_areas()
    ]
    return render_template(
        'index.html',
        title='House Tour',
        description='Ontdek de verschillende ruimtes van het huis.',
        areas=area_list,
        show_quiz=True
    )
