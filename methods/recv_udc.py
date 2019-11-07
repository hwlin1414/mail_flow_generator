import os
import socket
import select
import datetime

import mail

def recv_data(sock):
    data = ""
    while True:
        new_data = sock.recv(8192)
        if len(new_data) == 0: break
        data += new_data.decode('UTF-8')
    return data

def recv_udc(runtime, config):
    server_address = "{}/{}".format(config['udc_path'], config['token'].val())
    try:
        os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(server_address)
    os.chmod(server_address, 0o666)
    sock.listen(1)
    connection = None

    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    while runtime['ThreadStopFlag'] is False:
        rl, wl, el = select.select([sock], [], [], runtime['CheckFlagPeriod'])
        if len(rl) != 0:
            connection, client_address = sock.accept()
            data = recv_data(connection)
            connection.close()
            sock.close()
            os.unlink(server_address)
            return data
        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break

    if connection is not None: connection.close()
    sock.close()
    os.unlink(server_address)
    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('RECV timeout')

def recv(runtime, config):
    try:
        data = recv_udc(runtime, config)
        config['mail_msg_recv'] = mail.Mail.from_str(data)
        reason = mail.Mail.isbounce(config['mail_msg_recv'])
        if reason is not None:
            raise RuntimeError(reason)
    except RuntimeError as err:
        config['errors'].append(err)
    except TimeoutError as err:
        config['errors'].append(err)
