
from config import settings
from pydantic import BaseModel, EmailStr
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('templates'))


def send_email(receiver_email, subject, context, template_name):
   
    template = template_env.get_template(template_name)
    html_content = template.render(context)

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.noreply_email
    message["To"] = receiver_email

    part = MIMEText(html_content, "html")
    message.attach(part)
  
    server = smtplib.SMTP(settings.smtp_server, settings.smtp_server_port)
    server.set_debuglevel(1)
    server.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
    server.login(settings.smtp_server_username, settings.smtp_server_password)
    server.sendmail(
        settings.noreply_email, receiver_email, message.as_string()
    )
  
    return {"msg":"send mail"}