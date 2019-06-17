import os
import sys
import datetime
import traceback
import random
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mail
import send_smtp
import recv_imap

def run(runtime, config):
    try:
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        config['token'] = token

        msg = mail.Mail(**config)
        runtime['log'].info('generate token {}'.format(token))
        start = datetime.datetime.now()

        send_smtp.send(runtime, config, msg.as_string())
        if runtime['ThreadStopFlag'] is True: return

        recv_imap.recv(runtime, config)
        if runtime['ThreadStopFlag'] is True: return

        end = datetime.datetime.now()
        rtt = end - start
        runtime['log'].info('retrieve token {}, rtt {}'.format(token, rtt.total_seconds()))
    except TimeoutError:
        runtime['log'].error('Email {token} Timeout!'.format(token = token))
    except:
        err = sys.exc_info()
        runtime['log'].error('Unexpected error {}:{}, tb: {}'.format(
            err[0],
            err[1],
            ','.join(traceback.format_tb(err[2]))
        ))

