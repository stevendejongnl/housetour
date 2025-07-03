
from flask import Blueprint, render_template, current_app
import os
import frontmatter

area_blueprint = Blueprint('area', __name__, template_folder='templates', url_prefix='/area')

AREAS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data',
    'areas',
)

def get_available_areas():
    area_files = [f for f in os.listdir(AREAS_DIR) if f.endswith('.md')]
    return [f[:-3] for f in area_files]


def get_area_metadata(area_name):
    md_path = os.path.join(AREAS_DIR, f"{area_name}.md")
    meta = {'title': area_name.replace('_', ' ').replace('-', ' ').title(), 'description': ''}
    try:
        post = frontmatter.load(md_path)
        if isinstance(post.metadata, dict):
            meta.update(post.metadata)
    except Exception as e:
        current_app.logger.info(f"Kon metadata niet lezen uit {md_path}: {e}")
    return meta


@area_blueprint.route('/<area_name>')
def area_dynamic(area_name):
    if area_name not in get_available_areas():
        return render_template('404.html'), 404
    md_path = os.path.join(AREAS_DIR, f"{area_name}.md")
    md_html = ''
    try:
        post = frontmatter.load(md_path)
        import markdown
        md_html = markdown.markdown(post.content, extensions=['extra', 'nl2br'])
        current_app.logger.info(md_html)
    except Exception as e:
        current_app.logger.info(f"Kon markdown niet lezen: {e}")
    meta = get_area_metadata(area_name)
    current_app.logger.info(meta)
    data = {
        'title': meta.get('title', area_name),
        'description': meta.get('description', ''),
        'markdown_content': md_html if md_html else '<p><em>Geen content beschikbaar voor dit gebied.</em></p>'
    }
    return render_template('area.html', **data)