from tools.send_sms import send_sms
from tools.send_whatsapp import send_whatsapp


async def execute(recommendation: dict, profile: dict) -> str:
    product = recommendation.get("product", {})
    message = recommendation.get("message", "")

    # In production, map call_sid/phone from memory or Exotel payload
    phone_number = profile.get("phone_number", "test")

    sms_status = send_sms(phone_number, message)
    wa_status = send_whatsapp(phone_number, message)

    return f"{message} (sms={sms_status}, whatsapp={wa_status})"
