from flask import Blueprint, render_template
import os
from .markdown_utils import load_area_markdown

area_blueprint = Blueprint('area', __name__, template_folder='templates', url_prefix='/area')

AREAS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data',
    'areas',
)

def get_available_areas():
    area_files = [f for f in os.listdir(AREAS_DIR) if f.endswith('.md')]
    return [f[:-3] for f in area_files]

def get_area_title(area_name):
    return area_name.replace('_', ' ').replace('-', ' ').title()

@area_blueprint.route('/<area_name>')
def area_dynamic(area_name):
    if area_name not in get_available_areas():
        return render_template('404.html'), 404
    md_html = load_area_markdown(area_name)
    data = {
        'title': get_area_title(area_name),
        'area_name': area_name,
        'markdown_content': md_html if md_html else '<p><em>Geen content beschikbaar voor dit gebied.</em></p>'
    }
    return render_template('area.html', **data)