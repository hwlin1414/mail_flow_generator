import os
import sys
import socket

import settings
import logger
import methods.mail

appname = 'MailFlowGenerator'
# log instance, we need to log something in signal handler
#log = logger.logger(appname, os.path.dirname(os.path.abspath(__file__)) + '/app.log')

def main(mailtext):
    config = settings.read()
    mail = methods.mail.Mail.from_str(mailtext)
    if mail['X-MMF-TOKEN'] is None:
        #log.error("mail doesn't have X-MMF-TOKEN")
        with open('{}/mail'.format(config['DEFAULT']['ipc_path']), 'w') as f:
            f.write(mailtext)
            f.write('========\n')
        os.chmod('{}/mail'.format(config['DEFAULT']['ipc_path']), 0o777)
        sys.exit(1)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        #log.info("connect to {}/{}".format(config['DEFAULT']['ipc_path'], mail['X-MMF-TOKEN']))
        sock.connect("{}/{}".format(config['DEFAULT']['ipc_path'], mail['X-MMF-TOKEN']))
        sock.sendall(mailtext.encode('UTF-8'))
        sock.close()
    except socket.error as err:
        #log.error(err)
        sys.exit(1)

if __name__ == "__main__":
    mailtext = ''.join(sys.stdin.readlines())
    main(mailtext)

