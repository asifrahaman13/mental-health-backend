from config.config import sender_email, sender_password, homepage_url
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = sender_email
SENDER_PASSWORD = sender_password
HOME_PAGE_URL = homepage_url


def send_verification_email(email, token, type_of_verification):
    # Your email sending logic here, e.g., using SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = SENDER_EMAIL
    smtp_password = SENDER_PASSWORD

    subject = "Verify Your Email Address"
    sender_email = SENDER_EMAIL

    # Create a unique verification link with a token
    verification_link = f"{HOME_PAGE_URL}/{type_of_verification}?token={token}"

    # Compose the email message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = email
    message["Subject"] = subject

    text = f"Please click the following link to verify your email address: {verification_link}"
    message.attach(MIMEText(text, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send verification email: {str(e)}")
