import os
import sys
import datetime
import traceback
import random
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mail
import send_smtp
import smtplib
import recv_ipc

def run(runtime, config):
    try:
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        config['token'] = token

        msg = mail.Mail(**config)
        runtime['log'].info('generate token {}'.format(token))
        start = datetime.datetime.now()

        # Trying send emails
        try:
            send_smtp.send(runtime, config, msg.as_string())
            if runtime['ThreadStopFlag'] is True: return
        # Capture known SMTP exceptions
        except (smtplib.SMTPRecipientsRefused, ) as err:
            if 'smtp_expect' in config and config['smtp_expect'] in str(err):
                for r in err.recipients:
                    msg = err.recipients[r][1].decode('UTF-8')
                    runtime['log'].info('{} successfully get "{}"'.format(config['name'], msg))
                return
            raise
        # If exception expected but not happen
        if 'smtp_expect' in config and config['smtp_expect'] != "":
            runtime['log'].error('email sent'.format(token))
            return

        # Regular mail, trying retrieve
        recv_ipc.recv(runtime, config)
        if runtime['ThreadStopFlag'] is True: return

        end = datetime.datetime.now()
        rtt = end - start
        runtime['log'].info('retrieve token {}, rtt {:.2f}'.format(token, rtt.total_seconds()))
    except TimeoutError:
        runtime['log'].error('Email {} Timeout!'.format(token))
    except:
        err = sys.exc_info()
        runtime['log'].error('Unexpected error {}:{}, tb: {}'.format(
            err[0],
            err[1],
            ','.join(traceback.format_tb(err[2]))
        ))
