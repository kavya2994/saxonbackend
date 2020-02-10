import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_email(to_address, subject, body):
    return requests.post(
		"https://api.mailgun.net/v3/sandbox7ecc85d60c624a9dac88f9a0b159875e.mailgun.org/messages",
		auth=("api", "key-5146dc1e64f457fde62c94efb7a06388"),
		data={
            "from": "Test User <test@sandbox7ecc85d60c624a9dac88f9a0b159875e.mailgun.org>",
			"to": [to_address],
			"subject": subject,
			"html": body
        }
    )
    # smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
    # smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")

    # msg = MIMEMultipart()
    # msg['subject'] = subject
    # msg['from'] = "venkatesh"
    # msg['to'] = "venkatesh"
    # from_address = "venkateshvyyerram@gmail.com"

    # msgtext = MIMEText(body, 'html')
    # msg.attach(msgtext)

    # smtpObj.sendmail(from_addr=from_address, to_addrs=to_address, msg=msg.as_string())
