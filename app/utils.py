import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    msg = MIMEMultipart()
    msg['From'] = current_app.config['MAIL_USERNAME']
    msg['To'] = email
    msg['Subject'] = "Your OTP for Login"
    
    body = f"Your OTP is: {otp}"
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
    server.starttls()
    server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
    text = msg.as_string()
    server.sendmail(current_app.config['MAIL_USERNAME'], email, text)
    server.quit()