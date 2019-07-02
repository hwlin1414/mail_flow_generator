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
    token = mail['X-MMF-TOKEN']
    if token is None:
        # if this mail is bounced message
        if mail.get_content_type() == "multipart/report":
            for part in mail.walk():
                if part.get_content_type() == "message/rfc822":
                    p = part.get_payload()[0]
                    token = p['X-MMF-TOKEN']

        # if still cannot find token
        if token is None:
            # not bounced message
            #log.error("mail doesn't have X-MMF-TOKEN")
            with open('{}/mail'.format(config['DEFAULT']['ipc_path']), 'w') as f:
                f.write(mailtext)
                f.write('========\n')
            os.chmod('{}/mail'.format(config['DEFAULT']['ipc_path']), 0o777)
            sys.exit(1)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        #log.info("connect to {}/{}".format(config['DEFAULT']['ipc_path'], token))
        sock.connect("{}/{}".format(config['DEFAULT']['ipc_path'], token))
        sock.sendall(mailtext.encode('UTF-8'))
        sock.close()
    except socket.error as err:
        #log.error(err)
        sys.exit(1)

if __name__ == "__main__":
    mailtext = ''.join(sys.stdin.readlines())
    main(mailtext)

