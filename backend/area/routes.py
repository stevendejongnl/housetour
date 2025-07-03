from flask import Blueprint, render_template



from .kitchen import kitchen
from .living_room import living_room
from .markdown_utils import load_area_markdown

area_blueprint = Blueprint('area', __name__, template_folder='templates', url_prefix='/area')


# Mapping van area-namen naar hun functies en templates
area_map = {
    'living-room': {
        'func': living_room,
        'template': 'area/living-room.html',
    },
    'kitchen': {
        'func': kitchen,
        'template': 'area/kitchen.html',
    },
}


@area_blueprint.route('/<area_name>')
def area_dynamic(area_name):
    area = area_map.get(area_name)
    if not area:
        return render_template('404.html'), 404
    data = area['func']()
    # Markdown content inlezen en toevoegen aan data
    md_html = load_area_markdown(area_name)
    if md_html:
        data['markdown_content'] = md_html
    else:
        data['markdown_content'] = '<p><em>Geen content beschikbaar voor dit gebied.</em></p>'
    return render_template('area.html', **data)