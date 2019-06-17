import os
import time
import datetime
import imaplib
import socket

def recv(runtime, config):
    socket.setdefaulttimeout(3)

    imap = imaplib.IMAP4_SSL(config['imap_host'])
    imap.login(config['imap_user'], config['imap_password'])
    imap.select()
    if 'imap_folder' in config: imap.select(config['imap_folder'])

    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    while runtime['ThreadStopFlag'] is False:
        data = imap.search(None, '(HEADER X-MMF-TOKEN "{}")'.format(config['token']))
        if len(data[1][0]) != 0:
            imap.close()
            imap.logout()
            return

        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break
        time.sleep(runtime['CheckFlagPeriod'])

    imap.close()
    imap.logout()
    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('IMAP timeout')
