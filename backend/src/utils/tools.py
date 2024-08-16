import qrcode
import base64
from io import BytesIO
import secrets
import string

from src.config.settings import settings

def get_random_string(len:int = 6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(len))

def get_random_num(len:int = 6):
    return ''.join(secrets.choice(string.digits) for _ in range(len))


def generate_card_qr_code(uuid:str,code:str):
    qr = qrcode.QRCode( # type: ignore
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L, # type: ignore
        box_size=10,
        border=4,
    )
    data = f'{settings.BASE_URL}/card-use/{uuid}/{code}'
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')
