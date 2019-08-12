import sys
import mysmtp as smtplib

def connect(runtime, config):
    if config['smtp_protocol'] == "smtp":
        port = config['smtp_port'] if 'smtp_port' in config else 25
        smtp = smtplib.SMTP(config['smtp_host'], port, timeout = 5)
    elif config['smtp_protocol'] == "smtps":
        port = config['smtp_port'] if 'smtp_port' in config else 465
        smtp = smtplib.SMTP_SSL(config['smtp_host'], port, timeout = 5)
    else:
        raise ValueError("unknown Protocol")
    smtp.ehlo_or_helo_if_needed()
    if 'smtp_starttls' in config and config['smtp_starttls'] is True:
        smtp.starttls()
    return smtp

def auth(runtime, config, smtp):
    if config['smtp_user'] is not False:
        smtp.login(config['smtp_user'], config['smtp_password'])

def send(runtime, config):
    try:
        smtp = connect(runtime, config)
        auth(runtime, config, smtp)
        result = smtp.sendmail(
            config['smtp_sender'],
            config['smtp_recipients'],
            config['mail_msg_send'].as_string()
        )
        smtp.quit()
        config['send_result'] = result
        if 'smtp_expect' in config:
            raise RuntimeError('expect error "{}" but message sent.'.format(config['smtp_expect']))
    except (smtplib.SMTPServerDisconnected, ) as err:
        config['errors'].append(err)
    except (smtplib.SMTPRecipientsRefused, ) as err:
        if 'smtp_expect' in config and config['smtp_expect'] in str(err):
            for r in err.recipients:
                msg = err.recipients[r][1].decode('UTF-8')
                runtime['log'].info('{} successfully get reject "{}"'.format(config['token'], msg))
            return
        config['errors'].append(err)
    except RuntimeError as err:
        config['errors'].append(err)
