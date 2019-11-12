import sys
import mysmtp as smtplib

DEF_SMTP_TIMEOUT = 10

# connect to smtp server
def connect(runtime, config):
    # if protocol is smtp
    if config['smtp_protocol'] == "smtp":
        port = config['smtp_port'] if 'smtp_port' in config else 25
        smtp = smtplib.SMTP(config['smtp_host'], port, timeout = DEF_SMTP_TIMEOUT)
    # if protocol is smtp with ssl
    elif config['smtp_protocol'] == "smtps":
        port = config['smtp_port'] if 'smtp_port' in config else 465
        smtp = smtplib.SMTP_SSL(config['smtp_host'], port, timeout = DEF_SMTP_TIMEOUT)
    # other unknown value
    else:
        raise ValueError("unknown Protocol")
    # if server need helo or ehlo
    smtp.ehlo_or_helo_if_needed()

    # if server need starttls
    if 'smtp_starttls' in config and config['smtp_starttls'] is True:
        smtp.starttls()
    return smtp

def auth(runtime, config, smtp):
    # smtp auth here
    if config['smtp_user'] is not False:
        smtp.login(config['smtp_user'], config['smtp_password'])

def send(runtime, config):
    try:
        # connect to smtp server
        smtp = connect(runtime, config)
        # auth
        auth(runtime, config, smtp)
        # send email to all
        result = smtp.sendmail(
            config['smtp_sender'],
            config['smtp_recipients'],
            config['mail_msg_send'].as_string()
        )
        # smtp quit
        smtp.quit()

        # return value handling
        config['send_result'] = result
        # expect error, but message sent
        if 'smtp_expect' in config:
            raise RuntimeError('expect error "{}" but message sent.'.format(config['smtp_expect']))
    # recipient refused
    except (smtplib.SMTPRecipientsRefused, ) as err:
        # if expect message not send
        if 'smtp_expect' in config and config['smtp_expect'] in str(err):
            # find reject message
            for r in err.recipients:
                msg = err.recipients[r][1].decode('UTF-8')
                runtime['log'].info('{} successfully get reject "{}"'.format(config['token'], msg))
            return
        config['errors'].append(err)
    # other error or refuse
    except (smtplib.SMTPConnectError,
        smtplib.SMTPAuthenticationError,
        smtplib.SMTPServerDisconnected,
        smtplib.SMTPException,
    ) as err:
        config['errors'].append(err)
    # runtime error when unexpected send email
    except RuntimeError as err:
        config['errors'].append(err)
