import sys
import smtplib
import email
import email.mime
import email.mime.text
import email.mime.multipart
import email.mime.base
import email.utils

def msgtext(config):
    errmsg = ''
    for err in config['errors']:
        errmsg += 'Unexpected error {}: {}'.format(type(err), str(err))

    return """
{errmsg}
""".format(errmsg = errmsg)

def err(runtime, config):
    if 'errors' not in config or len(config['errors']) == 0: return

    errtitle = 'Mailmon Error {}'.format(config['token'])

    msg = email.mime.multipart.MIMEMultipart()
    text = msgtext(config)
    text = email.mime.text.MIMEText(text)
    msg.attach(text)
    msg['Subject'] = errtitle
    msg['Message-Id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    msg['From'] = config['err_sender']
    msg['To'] = ', '.join(config['err_recipients'])

    smtp = smtplib.SMTP('localhost', 25)
    smtp.ehlo_or_helo_if_needed()

    result = smtp.sendmail(config['err_sender'], config['err_recipients'], msg.as_string())
    smtp.quit()
