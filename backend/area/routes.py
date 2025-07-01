from flask import Blueprint, render_template

from .kitchen import kitchen
from .living_room import living_room

area_blueprint = Blueprint('area', __name__, template_folder='templates', url_prefix='/area')

@area_blueprint.route('/living-room')
def area_living_room():
    living_room_data = living_room()
    return render_template(
        'area/living-room.html',
        **living_room_data,
    )


@area_blueprint.route('/kitchen')
def area_kitchen():
    kitchen_data = kitchen()
    return render_template(
        'area/kitchen.html',
        **kitchen_data,
    )