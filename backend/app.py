from flask import Flask, render_template
from area.routes import area_blueprint

__version__ = '0.1.0'
app = Flask(__name__)
app.secret_key = 'mega-secret-housetour'

app.register_blueprint(area_blueprint)

@app.route('/')
def index():
    area_urls = [
        rule.rule
        for rule in app.url_map.iter_rules()
        if rule.endpoint.startswith(f'{area_blueprint.name}.')
    ]
    return render_template(
        'index.html',
        title='House Tour',
        description='Explore the different areas of the house.',
        area_urls=area_urls
    )