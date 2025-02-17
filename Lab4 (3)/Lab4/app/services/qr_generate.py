import segno
import base64
from io import BytesIO
from app.models import Calculation

def generate_calculation_qr(calculation):
    status_dict = dict(Calculation.STATUS_CHOICES)

    info = (
        f"Запрос №{calculation.id}\n"
        f"Создатель: {calculation.owner.username if calculation.owner else 'Неизвестен'}\n"
        f"Статус: {status_dict.get(calculation.status, 'Неизвестен')}\n"
    )

    if calculation.date_created:
        info += f"Дата создания: {calculation.date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
    if calculation.date_formation:
        info += f"Дата формирования: {calculation.date_formation.strftime('%Y-%m-%d %H:%M:%S')}\n"
    if calculation.date_complete:
        info += f"Дата завершения: {calculation.date_complete.strftime('%Y-%m-%d %H:%M:%S')}\n"

    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return qr_image_base64
