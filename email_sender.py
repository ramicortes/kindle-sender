import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

def send_email(config, subject, body, attachment_path):
    """Send email with attachment using config settings."""
    print("Sending email...")
    from_email = config['Email']['from_email']
    password = config['Email']['password']
    to_email = config['Email']['kindle_email']
    smtp_server = config['Email']['smtp_server']
    smtp_port = int(config['Email']['smtp_port'])
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body))
    
    # Attach the file
    with open(attachment_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 
                        f'attachment; filename="{os.path.basename(attachment_path)}"')
        msg.attach(part)
    
    try:
        # Send email
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.login(from_email, password)
        smtp.sendmail(from_email, to_email, msg.as_string())
        smtp.close()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
