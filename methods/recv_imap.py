import os
import time
import datetime
import imaplib
import socket

import mail

def recv_imap(runtime, config):
    # set socket default value
    socket.setdefaulttimeout(5)

    # connect to imap server
    imap = imaplib.IMAP4_SSL(config['imap_host'])
    # login imap server
    imap.login(config['imap_user'], config['imap_password'])
    # select mbox
    imap.select()
    if 'imap_folder' in config: imap.select(config['imap_folder'])

    # while loop, calc start time and timeout time.
    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    while runtime['ThreadStopFlag'] is False:
        # search X-MMF-TOKEN header
        data = imap.search(None, '(HEADER X-MMF-TOKEN "{}")'.format(config['token'].val()))
        msgs = data[1][0].split()
        # if found message contain that header
        if len(msgs) != 0:
            imap.select()
            if 'imap_folder' in config: imap.select(config['imap_folder'])
            data = imap.search(None, '(HEADER X-MMF-TOKEN "{}")'.format(config['token'].val()))
            msgs = data[1][0].split()
            # fetch message for return
            typ, msg = imap.fetch(msgs[0], '(RFC822)')
            msg = msg[0][1].decode('UTF-8')
            # if need reserve or delete mail
            if 'imap_reserve' not in config:
                imap.store(msgs[0], '+FLAGS', '\\Deleted')
                imap.expunge()

            # close socket
            imap.close()
            imap.logout()
            # return email
            return msg
        # email not found, sleep a while
        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break
        time.sleep(runtime['CheckFlagPeriod'])

    # timeout, close socket and raise event
    imap.close()
    imap.logout()
    # raise timeout event
    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('IMAP timeout')

def recv(runtime, config):
    try:
        data = recv_imap(runtime, config)
        # parse return value to mail received (for analysis)
        config['mail_msg_recv'] = mail.Mail.from_str(data)
    except TimeoutError as err:
        # error handling
        config['errors'].append(err)
