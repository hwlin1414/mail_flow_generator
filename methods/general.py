import os
import sys
import datetime
import traceback
import random
import string
import importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mail

class Token():
    def __init__(self, name, **kwargs):
        self.name = name
        self.token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    def val(self):
        return self.token
    def __str__(self):
        return "{}/{}".format(self.name, self.token)

def loadfunc(runtime, modclass, modname):
    try:
        # load module(when first execute this line)
        mod = importlib.import_module('{}_{}'.format(modclass, modname))
        # reload module(to ensure load new module when programmer change code)
        mod = importlib.reload(mod)
        func = getattr(mod, modclass)
        return func
    except ImportError as msg:
        runtime['log'].error(msg)

def run(runtime, config):
    config['token'] = Token(**config)
    config['errors'] = []
    # Mail
    config['mail_msg_send'] = mail.Mail(config)

    # send
    runtime['log'].info('sending token {}'.format(config['token']))
    config['start'] = datetime.datetime.now()
    if len(config['errors']) == 0:
        func = loadfunc(runtime, 'send', config['send'])
        func(runtime, config)
    if runtime['ThreadStopFlag'] is True: return

    # recv
    if len(config['errors']) == 0 and config['recv'] != '':
        func = loadfunc(runtime, 'recv', config['recv'])
        func(runtime, config)
    if runtime['ThreadStopFlag'] is True: return
    config['end'] = datetime.datetime.now()
    rtt = config['end'] - config['start']
    if len(config['errors']) == 0 and config['recv'] != '':
        runtime['log'].info('retrieve token {}, rtt {:.2f}'
            .format(config['token'], rtt.total_seconds()))

    # analysis
    if len(config['errors']) == 0 or 'analysis_error' in config:
        for analysis in config['analysis'].split():
            func = loadfunc(runtime, 'analysis', analysis)
            func(runtime, config)
            if runtime['ThreadStopFlag'] is True: return

    # err log
    if len(config['errors']) != 0:
        for err in config['errors']:
            errtitle = '{} Unexpected error {}'.format(config['token'], type(err))
            errmsg = str(err)
            runtime['log'].error('{}: {}'.format(errtitle, errmsg))
    if runtime['ThreadStopFlag'] is True: return
    # err counter
    threaddata = runtime['threaddata'][config['name']]
    if len(config['errors']) == 0:
        threaddata['lock'].acquire()
        threaddata['err_counter'] = 0
        err_counter = 0
        threaddata['lock'].release()
    else:
        threaddata['lock'].acquire()
        if 'err_counter' not in threaddata:
            threaddata['err_counter'] = 0
        threaddata['err_counter'] += 1
        err_counter = threaddata['err_counter']
        threaddata['lock'].release()
    # err
    if err_counter > 0 and err_counter >= config['err_threshold']:
        for err in config['err'].split():
            func = loadfunc(runtime, 'err', err)
            func(runtime, config)
            if runtime['ThreadStopFlag'] is True: return
