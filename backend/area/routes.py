import os

import frontmatter
import markdown
from flask import Blueprint, render_template, current_app, redirect, url_for

area_blueprint = Blueprint('area', __name__, template_folder='templates', url_prefix='/area')

AREAS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data',
    'areas',
)


def normalize(s):
    return s.replace('-', '').replace('_', '').lower()


def get_available_areas() -> list[str]:
    area_files = [file for file in os.listdir(AREAS_DIR) if file.endswith('.md')]

    def extract_number(file):
        if '-' in file and file[:2].isdigit() and file[2] == '-':
            return int(file[:2])
        return float('inf')

    area_files.sort(key=extract_number)
    areas = []
    for file in area_files:
        name = file[:-3]
        if '-' in name and name[:2].isdigit() and name[2] == '-':
            name = name[3:]
        areas.append(name)
    return areas


def get_area_file(area_name: str = None) -> str | None:
    current_app.logger.info(f"Searching for area file for: {area_name}")
    return next(
        (
            file for file in os.listdir(AREAS_DIR)
            if file.endswith('.md') and file.removeprefix(
            file[:3] if file[:2].isdigit() and file[2] == '-' else ''
        )[:-3] == area_name),
        None
    )


def load_area_metadata(area_name: str, md_file: str) -> dict:
    md_path = os.path.join(AREAS_DIR, md_file)
    meta = {'title': area_name.replace('_', ' ').replace('-', ' ').title(), 'description': ''}
    try:
        post = frontmatter.load(md_path)
        if isinstance(post.metadata, dict):
            lowercased_meta = {k.lower(): v for k, v in post.metadata.items()}
            meta.update(lowercased_meta)
    except Exception as e:
        current_app.logger.info(f"Could not read metadata from {md_path}: {e}")

    return meta


def get_area_metadata(area_name: str) -> dict:
    md_file = get_area_file(area_name)
    current_app.logger.info(f"Looking for area metadata for {area_name}, found file: {md_file}")
    if not md_file:
        return {'title': area_name.replace('_', ' ').replace('-', ' ').title(), 'description': ''}

    return load_area_metadata(area_name, md_file)


def get_area_content(area_name: str) -> str:
    md_file = get_area_file(area_name)
    if not md_file:
        return ''

    md_path = os.path.join(AREAS_DIR, md_file)
    try:
        with open(md_path, encoding='utf-8') as f:
            content = f.read()
            post = frontmatter.loads(content)
            md_content = post.content if isinstance(post.content, str) else ''
            html_content = markdown.markdown(md_content, extensions=['nl2br'])
            return html_content
    except Exception as e:
        current_app.logger.info(f"Could not read content from {md_path}: {e}")
        return ''


def is_exact_image(img: str, area_name: str) -> bool:
        basename = img.split('-')[0] if '-' in img else img.split('.')[0]
        return basename == area_name
    

def get_area_images(area_name: str) -> list[str]:
    static_dir = os.path.join(current_app.static_folder, 'areas')
    return [
        f'/static/areas/{img}'
        for img in os.listdir(static_dir)
        if is_exact_image(img, area_name) and img.endswith(('.jpg', '.jpeg', '.png', '.gif'))
    ]


@area_blueprint.route('/<area_name>')
def area_dynamic(area_name: str) -> str:
    available_areas = get_available_areas()
    if area_name not in available_areas:
        normalized_input = normalize(area_name)
        matches = [a for a in available_areas if normalize(a) == normalized_input]
        if len(matches) == 1:
            return redirect(url_for('area.area_dynamic', area_name=matches[0]))
        return render_template('404.html'), 404

    meta = get_area_metadata(area_name)
    content = get_area_content(area_name)

    current_app.logger.info(f"{meta=}, {content=}")

    images = get_area_images(area_name)
    data = {
        'title': meta.get('title', area_name),
        'description': meta.get('description', ''),
        'markdown_content': content,
        'images': images,
        'images_count': len(images),
    }
    return render_template('area.html', **data)
