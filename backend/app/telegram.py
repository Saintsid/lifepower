import httpx
import os
from typing import Optional

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_notification(message: str) -> bool:
    """
    Отправляет уведомление в Telegram
    Возвращает True если успешно, False если ошибка
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                print("✅ Telegram notification sent")
                return True
            else:
                print(f"❌ Telegram API error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")
        return False


async def notify_new_booking(booking_data: dict, user_name: Optional[str] = None):
    """
    Отправляет уведомление о новой заявке
    """
    user_type = "🔐 Зарегистрированный пользователь" if user_name else "👤 Анонимная заявка"
    
    referral_info = ""
    referral_source = booking_data.get('referral_source')
    if referral_source:
        if referral_source == 'recommendation' and booking_data.get('referral_person'):
            referral_info = f"\n<b>Откуда узнали:</b> Рекомендация знакомых ({booking_data.get('referral_person')})"
        elif referral_source == 'other' and booking_data.get('referral_other'):
            referral_info = f"\n<b>Откуда узнали:</b> {booking_data.get('referral_other')}"
        else:
            referral_labels = {
                'internet_search': 'Интернет-поиск (Яндекс, Google)',
                'social_media': 'Социальные сети',
                'recommendation': 'Рекомендация знакомых',
                'outdoor_advertising': 'Наружная реклама',
                'previous_clients': 'От предыдущих клиентов'
            }
            referral_info = f"\n<b>Откуда узнали:</b> {referral_labels.get(referral_source, referral_source)}"
    
    message = f"""
🆕 <b>Новая заявка на консультацию!</b>

{user_type}

<b>Имя:</b> {booking_data.get('name', '-')}
<b>Телефон:</b> {booking_data.get('phone', '-')}
<b>Email:</b> {booking_data.get('email', '-')}
<b>Услуга:</b> {booking_data.get('service', 'Не указана')}
<b>Сообщение:</b> {booking_data.get('message', '-')}{referral_info}

📊 Статус: Новая
🕐 Время: {booking_data.get('created_at', '-')}
"""
    
    await send_telegram_notification(message.strip())
