import os
import sys
import datetime
import traceback
import random
import string

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mail
import send_smtp
import recv_pop3
import anal_header

def run(runtime, config):
    try:
        config['token'] = mail.Token(**config)

        msg = mail.Mail(**config)
        runtime['log'].info('generate token {}'.format(config['token']))
        start = datetime.datetime.now()

        send_smtp.send(runtime, config, msg.as_string())
        if runtime['ThreadStopFlag'] is True: return

        msg = recv_pop3.recv(runtime, config)
        if runtime['ThreadStopFlag'] is True: return

        end = datetime.datetime.now()
        rtt = end - start
        runtime['log'].info('retrieve token {}, rtt {:.2f}'.format(config['token'], rtt.total_seconds()))

        anal_header.anal(runtime, config, msg)
    except TimeoutError:
        runtime['log'].error('Email {} Timeout!'.format(config['token']))
    except:
        err = sys.exc_info()
        runtime['log'].error('Unexpected error {}:{}, tb: {}'.format(
            err[0],
            err[1],
            ','.join(traceback.format_tb(err[2]))
        ))


