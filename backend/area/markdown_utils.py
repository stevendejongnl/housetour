import os
import markdown

def strip_yaml_frontmatter(md_text):
    if md_text.startswith('---'):
        end = md_text.find('---', 3)
        if end != -1:
            return md_text[end+3:].lstrip('\r\n')
    return md_text

def load_area_markdown(area_name):
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md_path = os.path.join(base_path, 'data', 'areas', f'{area_name}.md')
    if not os.path.exists(md_path):
        return None
    with open(md_path, encoding='utf-8') as f:
        md_content = f.read()
    md_content = strip_yaml_frontmatter(md_content)
    html = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    return html
