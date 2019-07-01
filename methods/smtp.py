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
        config['token'] = mail.Token(**config)

        msg = mail.Mail(**config)
        runtime['log'].info('generate token {}'.format(config['token']))
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
                    runtime['log'].info('{} successfully get reject "{}"'.format(config['token'], msg))
                return
            raise
        # If exception expected but not happen
        if 'smtp_expect' in config and config['smtp_expect'] != "":
            runtime['log'].error('email {} sent'.format(config['token']))
            return

        # Regular mail, trying retrieve
        msg2 = recv_ipc.recv(runtime, config)
        msg2 = mail.Mail.from_str(msg2)
        if runtime['ThreadStopFlag'] is True: return

        end = datetime.datetime.now()
        rtt = end - start
        if 'X-MMF-TOKEN' not in msg2:
            runtime['log'].error('bounced token {}, rtt {:.2f}'.format(config['token'], rtt.total_seconds()))
        else:
            runtime['log'].info('retrieve token {}, rtt {:.2f}'.format(config['token'], rtt.total_seconds()))
    except TimeoutError:
        runtime['log'].error('Email {} Timeout!'.format(config['token']))
    except:
        err = sys.exc_info()
        runtime['log'].error('Unexpected error {}:{}, tb: {}'.format(
            err[0],
            err[1],
            ','.join(traceback.format_tb(err[2]))
        ))
