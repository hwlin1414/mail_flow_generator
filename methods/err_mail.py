import sys
import smtplib
import email
import email.mime
import email.mime.text
import email.mime.multipart
import email.mime.base
import email.utils

def err(runtime, config, errmsg):
    msgtext = """
        {err}
    """.format(err = errmsg)

    msg = email.mime.multipart.MIMEMultipart()
    text = email.mime.text.MIMEText(msgtext)
    msg.attach(text)
    msg['Subject'] = 'MailMonitorFramework: Error'
    msg['Message-Id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    msg['From'] = config['err_sender']
    msg['To'] = ', '.join(config['err_recipients'])

    smtp = smtplib.SMTP('localhost', 25)
    smtp.ehlo_or_helo_if_needed()

    result = smtp.sendmail(config['err_sender'], config['err_recipients'], msg)
    smtp.quit()
