import random


# ---------------------------------------------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# ---------------------------------------------------------------------
def send_sms(phone_number, otp):
    # Send otp to the phone_number using
    # an external API.
    pass
