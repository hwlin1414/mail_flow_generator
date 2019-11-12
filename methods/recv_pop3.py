import os
import time
import datetime
import poplib
import socket

import mail

def recv_pop3(runtime, config):
    # set socket default value
    socket.setdefaulttimeout(15)

    # while loop, calc start time and timeout
    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    while runtime['ThreadStopFlag'] is False:
        try:
            # conenct to pop3 ssl
            pop3 = poplib.POP3_SSL(config['pop3_host'], timeout = 15)
            # login into pop3 server
            pop3.user(config['pop3_user'])
            pop3.pass_(config['pop3_password'])

            # fetch mail list
            total = len(pop3.list()[1])
            # find last 15 mail
            if total > 15: checked = total - 15
            else: checked = 0

            # for i in last 15 mail
            for i in range(checked, total)[::-1]:
                #print("tryin fetch: {}".format(i))
                msg = ''
                # retreive email
                msglist = pop3.retr(i + 1)[1]
                for msgline in msglist:
                    try:
                        msg += "{}\n".format(msgline.decode('UTF-8'))
                    except:
                        pass
                #print(msg)
                # if find token in mail
                if config['token'].val() in msg:
                    # reserve mail or delete it
                    if 'pop3_reserve' not in config:
                        pop3.dele(i + 1)
                    # quit socket
                    pop3.quit()
                    return msg
            # quit socket
            pop3.quit()
        except socket.timeout:
            pass

        # if not found, sleep a while and restart
        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break
        time.sleep(runtime['CheckFlagPeriod'])

    # raisetimeout error
    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('POP3 timeout')

def recv(runtime, config):
    try:
        # recv mail from pop3
        data = recv_pop3(runtime, config)
        # parse mail from data for analysis
        config['mail_msg_recv'] = mail.Mail.from_str(data)
    except TimeoutError as err:
        # error handling
        config['errors'].append(err)
