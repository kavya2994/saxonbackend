import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_email(to_address, subject, body):
    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")

    msg = MIMEMultipart()
    msg['subject'] = subject
    msg['from'] = "venkatesh"
    msg['to'] = "venkatesh"
    from_address = "venkateshvyyerram@gmail.com"

    msgtext = MIMEText(body, 'html')
    msg.attach(msgtext)

    smtpObj.sendmail(from_addr=from_address, to_addrs=to_address, msg=msg.as_string())
