import sys
import mysmtp as smtplib

def send(runtime, config, msg):
    if config['smtp_protocol'] == "smtp":
        port = config['smtp_port'] if 'smtp_port' in config else 25
        smtp = smtplib.SMTP(config['smtp_host'], port, timeout = 5)
    elif config['smtp_protocol'] == "smtps":
        port = config['smtp_port'] if 'smtp_port' in config else 465
        smtp = smtplib.SMTP_SSL(config['smtp_host'], port, timeout = 5)
    else:
        raise ValueError("unknown Protocol")
    smtp.ehlo_or_helo_if_needed()
    if config['smtp_starttls'] is True: smtp.starttls()
    if config['smtp_user'] is not False: smtp.login(config['smtp_user'], config['smtp_password'])

    result = smtp.sendmail(config['sender'], config['recipients'], msg)
    smtp.quit()
    return result
