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

def run(runtime, config):
    try:
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        config['token'] = token

        config['sender'] = "{}.{rand}@{}".format(*(config['sender'].split('@')), rand = token)
        msg = mail.Mail(**config)
        try:
            send_smtp.send(runtime, config, msg.as_string())
        except smtplib.SMTPRecipientsRefused as msg:
            if config['smtp_except'] in str(msg):
                runtime['log'].info('{} successfully get {}'.format(config['name'], msg))
                return
            raise

        runtime['log'].error('email sent'.format(token))
    except:
        err = sys.exc_info()
        runtime['log'].error('Unexpected error {}:{}, tb: {}'.format(
            err[0],
            err[1],
            ','.join(traceback.format_tb(err[2]))
        ))
