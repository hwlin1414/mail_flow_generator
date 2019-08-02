import os
import time
import datetime
import poplib
import socket

def recv(runtime, config):
    socket.setdefaulttimeout(15)

    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    while runtime['ThreadStopFlag'] is False:
        try:
            pop3 = poplib.POP3_SSL(config['pop3_host'], timeout = 15)
            pop3.user(config['pop3_user'])
            pop3.pass_(config['pop3_password'])

            total = len(pop3.list()[1])
            if total > 15: checked = total - 15
            else: checked = 0

            for i in range(checked, total)[::-1]:
                #print("tryin fetch: {}".format(i))
                msg = ''
                msglist = pop3.retr(i + 1)[1]
                for msgline in msglist:
                    try:
                        msg += "{}\n".format(msgline.decode('UTF-8'))
                    except:
                        pass
                #print(msg)
                if config['token'].val() in msg:
                    if 'pop3_reserve' not in config:
                        pop3.dele(i + 1)
                    pop3.quit()
                    return msg
            pop3.quit()
        except socket.timeout:
            pass

        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break
        time.sleep(runtime['CheckFlagPeriod'])

    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('POP3 timeout')
