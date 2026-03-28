def send_sms(phone_number: str, message: str) -> str:
    # TODO: Integrate Exotel/other SMS gateway
    print(f"SMS to {phone_number}: {message}")
    return "queued"
