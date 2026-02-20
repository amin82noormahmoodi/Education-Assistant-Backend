import os
import secrets
import smtplib
from email.mime.text import MIMEText

def generate_otp(length=6):
    return "".join(str(secrets.randbelow(10)) for _ in range(length))

def otp_sender(receiver_email: str) -> str:
    sender_email = "aminnoormahmoodi2@gmail.com"
    sender_password = "szprvtmcsgnsatlq"
    otp_code = generate_otp()
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    message = MIMEText(f"Your OTP code is: {otp_code}")
    message["Subject"] = "OTP Code"
    message["From"] = sender_email
    message["To"] = receiver_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
    return otp_code