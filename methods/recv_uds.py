import os
import socket
import select
import datetime

import mail

def recv_data(sock):
    # receive data from socket
    data = ""
    while True:
        # socket buffer size 8192
        new_data = sock.recv(8192)
        if len(new_data) == 0: break
        # append date in utf-8
        data += new_data.decode('UTF-8')
    # returnd data
    return data

def recv_uds(runtime, config):
    # compose unix domain socket server address
    server_address = "{}/{}".format(config['uds_path'], config['token'].val())
    # try unlink old address
    try:
        os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise
    # create socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # bind socket
    sock.bind(server_address)
    # change mode for nobody to connect
    os.chmod(server_address, 0o666)
    # just wait for one client
    sock.listen(1)
    connection = None

    # ready for while loop
    start = datetime.datetime.now().replace(microsecond = 0)
    end = start + datetime.timedelta(seconds = config['timeout'])

    # While flag not set
    while runtime['ThreadStopFlag'] is False:
        # check if date avalible for read in socket
        rl, wl, el = select.select([sock], [], [], runtime['CheckFlagPeriod'])
        if len(rl) != 0:
            # accept connection
            connection, client_address = sock.accept()
            # read data in connection
            data = recv_data(connection)
            # close socket
            connection.close()
            sock.close()
            # unlink socket
            os.unlink(server_address)
            return data
        now = datetime.datetime.now().replace(microsecond = 0)
        if now >= end: break

    # close connection
    if connection is not None: connection.close()
    sock.close()
    os.unlink(server_address)
    # raise mail receive timeout
    if runtime['ThreadStopFlag'] is False:
        raise TimeoutError('RECV timeout')

def recv(runtime, config):
    try:
        # receive date from uds
        data = recv_uds(runtime, config)
        config['mail_msg_recv'] = mail.Mail.from_str(data)
        # check if mail is bounce
        reason = mail.Mail.isbounce(config['mail_msg_recv'])
        if reason is not None:
            # raise if mail is bounce
            raise RuntimeError(reason)
    except RuntimeError as err:
        # runtime error handling
        config['errors'].append(err)
    except TimeoutError as err:
        # runtime error handling
        config['errors'].append(err)
