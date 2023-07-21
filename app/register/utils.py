from email.message import EmailMessage
from flask import request
import jwt
from dotenv import load_dotenv
import smtplib
import os

load_dotenv()


def send_emails(email, token):
    sender = "pratikgopal.cha26@gmail.com"
    password = os.getenv("PASSWORD")
    receiver = email
    print(receiver)
    subject = "This is a test email"
    body = f"http://127.0.0.1:5000/verify?token={token}"

    em = EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        print("Testing this one")
        smtp.sendmail(sender, receiver, em.as_string())
        print("Sending email smtp")

    return True


def decode_the_token():
    email = jwt.decode(request.headers["token"], "zanc", algorithms="HS256")
    return email


print('testing')