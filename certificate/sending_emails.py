import smtplib
from email.mime.text import MIMEText
from django.conf import settings


TO = 'certificate@fossee.in'
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT
AUTH = 'LOGIN DIGEST-MD5 PLAIN'
EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD

def send_email(subject="Dummy",FROM_EMAIL="dummy@gmail.com",MESSAGE="Testing"):
	smtpserver = smtplib.SMTP(EMAIL_HOST,EMAIL_PORT)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo()
	smtpserver.esmtp_features['auth']= AUTH
	smtpserver.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
	msg = MIMEText(MESSAGE)
	msg['Subject'] = subject
	msg['From'] = FROM_EMAIL
	msg['To'] = TO
	try:
		smtpserver.sendmail(EMAIL_HOST_USER, TO, msg.as_string())
		smtpserver.close()
		return True
	except Exception as e:
		return False