import os
import time
import datetime
import imaplib
import socket

import mail

def recv_imap(runtime, config):
    socket.setdefaulttimeout(5)

    imap = imaplib.IMAP4_SSL(config['imap_host'])
    imap.login(config['imap_user'], config['imap_password'])
    imap.select()
    if 'imap_folder' in config: imap.select(config['imap_folder'])

    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    while runtime['ThreadStopFlag'] is False:
        data = imap.search(None, '(HEADER X-MMF-TOKEN "{}")'.format(config['token'].val()))
        msgs = data[1][0].split()
        if len(msgs) != 0:
            imap.select()
            if 'imap_folder' in config: imap.select(config['imap_folder'])
            data = imap.search(None, '(HEADER X-MMF-TOKEN "{}")'.format(config['token'].val()))
            msgs = data[1][0].split()

            typ, msg = imap.fetch(msgs[0], '(RFC822)')
            msg = msg[0][1].decode('UTF-8')

            if 'imap_reserve' not in config:
                imap.store(msgs[0], '+FLAGS', '\\Deleted')
                imap.expunge()

            imap.close()
            imap.logout()
            return msg

        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break
        time.sleep(runtime['CheckFlagPeriod'])

    imap.close()
    imap.logout()
    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('IMAP timeout')

def recv(runtime, config):
    try:
        data = recv_imap(runtime, config)
        config['mail_msg_recv'] = mail.Mail.from_str(data)
    except TimeoutError as err:
        config['errors'].append(err)
