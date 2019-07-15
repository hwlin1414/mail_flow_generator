import sys
import smtplib

def send(runtime, config, msg):
    if config['smtp_protocol'] == "smtp":
        smtp = smtplib.SMTP(config['smtp_host'], 25, timeout = 3)
    elif config['smtp_protocol'] == "smtps":
        smtp = smtplib.SMTP_SSL(config['smtp_host'], 465, timeout = 3)
    else:
        raise ValueError("unknown Protocol")
    smtp.ehlo_or_helo_if_needed()
    if config['smtp_starttls'] is True: smtp.starttls()
    if config['smtp_user'] is not False: smtp.login(config['smtp_user'], config['smtp_password'])

    result = smtp.sendmail(config['sender'], config['recipients'], msg)
    smtp.quit()
    return result
