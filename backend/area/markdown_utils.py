import os
import markdown

def load_area_markdown(area_name):
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md_path = os.path.join(base_path, 'data', 'areas', f'{area_name}.md')
    if not os.path.exists(md_path):
        return None
    with open(md_path, encoding='utf-8') as f:
        md_content = f.read()
    html = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    return html
