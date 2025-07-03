from flask import Blueprint, render_template, current_app
import os
import yaml
import markdown

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
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        if content.startswith('---'):
            end = content.find('\n---', 3)
            if end == -1:
                end = content.find('\r---', 3)
            if end != -1:
                meta_yaml = yaml.safe_load(content[3:end].strip())
                if isinstance(meta_yaml, dict):
                    meta.update(meta_yaml)
    except Exception as e:
        current_app.logger.info(f"Kon metadata niet lezen uit {md_path}: {e}")
    return meta

def strip_yaml_frontmatter(md_text):
    if md_text.startswith('---'):
        end = md_text.find('---', 3)
        if end != -1:
            return md_text[end+3:].lstrip('\r\n')
    return md_text

@area_blueprint.route('/<area_name>')
def area_dynamic(area_name):
    if area_name not in get_available_areas():
        return render_template('404.html'), 404
    raw_md = ''
    try:
        with open(os.path.join(AREAS_DIR, f"{area_name}.md"), encoding="utf-8") as f:
            raw_md = f.read()
    except Exception as e:
        current_app.logger.info(f"Kon markdown niet lezen: {e}")
    md_html = ''
    if raw_md:
        md_html = markdown.markdown(strip_yaml_frontmatter(raw_md), extensions=['extra', 'nl2br'])
        current_app.logger.info(md_html)
    meta = get_area_metadata(area_name)
    current_app.logger.info(meta)
    data = {
        'title': meta.get('title', area_name),
        'description': meta.get('description', ''),
        'markdown_content': md_html if md_html else '<p><em>Geen content beschikbaar voor dit gebied.</em></p>'
    }
    return render_template('area.html', **data)