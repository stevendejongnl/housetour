import importlib
import os
import sys
import segno
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter


TEXT_COLOR = '#345C64'
BACKGROUND_COLOR = '#ffE9C7'


def create_wifi_qr_code():
    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    if not ssid or not password:
        raise ValueError("Environment variables WIFI_SSID and WIFI_PASSWORD must be set.")

    data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    qr = segno.make(data)
    matrix_size = qr.symbol_size(1)[0]
    scale = 500 // matrix_size
    qr.save(
        out='/app/qr_codes/wifi.png',
        scale=scale,
        border=0,
        kind='png',
        dark=TEXT_COLOR,
        light=BACKGROUND_COLOR,
    )
    print(f"Generated WiFi QR code for SSID: {ssid}.")


def create_area_qr_code(area, base_url="https://housetour.madebysteven.nl"):
    data = f"{base_url}/area/{area}"
    qr = segno.make(data)
    matrix_size = qr.symbol_size(1)[0]
    scale = 500 // matrix_size
    qr.save(
        out=f'/app/qr_codes/{area}.png',
        scale=scale,
        border=0,
        kind='png',
        dark=TEXT_COLOR,
        light=BACKGROUND_COLOR,
    )
    print(f"Generated QR code for area: {area} at {data}.")


def load_font(font_path, size):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Font {font_path} not found. Using default font.")
        return ImageFont.load_default()


def draw_text(draw, text, position, font, fill=text_color):
    draw.text(position, text, fill=fill, font=font)


def tab(total_tabs:float=1, tab_size=4):
    tabs = tab_size * total_tabs

    return ' ' * int(tabs)


def generate_area_page(area, area_name, ssid, password, output_pdf_path, background_path="/app/qr_codes/background.png"):
    bg = Image.open(background_path).convert("RGB")
    draw = ImageDraw.Draw(bg)

    wifi_qr = Image.open('/app/qr_codes/wifi.png').convert("RGB").resize((350, 350))
    area_qr = Image.open(f'/app/qr_codes/{area}.png').convert("RGB").resize((350, 350))

    wifi_qr_pos = (120, 120)
    area_qr_pos = (bg.width // 2 + 50, 120)

    bg.paste(wifi_qr, wifi_qr_pos)
    bg.paste(area_qr, area_qr_pos)

    font_title = load_font("/usr/share/fonts/truetype/pacifico/Pacifico-Regular.ttf", 80)
    font_small = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    font_sub = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

    title_top_text = "Doe de"
    title_top_position = (bg.width // 2 - 200, bg.height // 2)
    draw_text(draw=draw, text=title_top_text, position=title_top_position, font=font_title)

    title_bottom_text = "House Tour!"
    title_bottom_position = (bg.width // 2 - 200, bg.height // 2 + 80)
    draw_text(draw=draw, text=title_bottom_text, position=title_bottom_position, font=font_title)

    wifi_qr_text = "Scan de QR-code voor Wi-Fi"
    wifi_qr_position = (wifi_qr_pos[0], wifi_qr_pos[1] + 360)
    draw_text(draw=draw, text=wifi_qr_text, position=wifi_qr_position, font=font_small)

    wifi_netwerk_text = f"Netwerk:{tab(total_tabs=2.8)}{ssid}"
    wifi_netwerk_position = (wifi_qr_pos[0], wifi_qr_pos[1] + 390)
    draw_text(draw=draw, text=wifi_netwerk_text, position=wifi_netwerk_position, font=font_sub)

    wifi_password_text = f"Wachtwoord:{tab()}{password}"
    wifi_password_position = (wifi_qr_pos[0], wifi_qr_pos[1] + 410)
    draw_text(draw=draw, text=wifi_password_text, position=wifi_password_position, font=font_sub)

    housetour_top_text = "Start de house Tour"
    housetour_top_position = (area_qr_pos[0], area_qr_pos[1] + 360)
    draw_text(draw=draw, text=housetour_top_text, position=housetour_top_position, font=font_small)

    housetour_bottom_text = f"in de {area_name}"
    housetour_bottom_position = (area_qr_pos[0], area_qr_pos[1] + 390)
    draw_text(draw=draw, text=housetour_bottom_text, position=housetour_bottom_position, font=font_sub)

    bg.save(output_pdf_path, "PDF")
    print(f"PDF gegenereerd: {output_pdf_path}")

if __name__ == "__main__":
    arguments = sys.argv[1:] if len(sys.argv) > 1 else []
    named_arguments = {arg.split('=')[0]: arg.split('=')[1] for arg in arguments if '=' in arg}

    wifi = named_arguments.get('wifi', None)

    if wifi:
        create_wifi_qr_code()

    areas_dir = os.path.join(os.path.dirname(__file__), '../data/areas')
    areas_list = [
        os.path.splitext(f)[0]
        for f in os.listdir(areas_dir)
        if f.endswith('.md') and not f.startswith('.')
    ]

    if areas_list:
        for area in areas_list:
            area = area.strip()
            create_area_qr_code(area)

            area_module_name = f'{area.replace("-", "_").lower()}'
            try:
                area_module = importlib.import_module(f"area.{area_module_name}")
            except ImportError:
                print(f"Module for area '{area}' not found. Skipping.")
                continue

            area_data = area_module.__dict__.get(area_module_name, None)
            area_data = area_data() if callable(area_data) else area_data

            generate_area_page(
                area=area,
                area_name=area_data.get('name', "NJope"),
                ssid=os.getenv("WIFI_SSID"),
                password=os.getenv("WIFI_PASSWORD"),
                output_pdf_path=f'/app/qr_codes/{area}.pdf',
            )
        exit(0)
