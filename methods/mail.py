import os
import string
import random
import email
import email.mime
import email.mime.text
import email.mime.multipart
import email.mime.base
import email.encoders
import email.utils
import email.parser

MSG = """
This is an email generated from Mail Monitor Framework
token: {token}
if you always see this email, please contact mailta@cs.nctu.edu.tw
"""

class Mail():
    # init mail object
    def __init__(self, config):
        token = config['token']
        # add message part
        self.msg = email.mime.multipart.MIMEMultipart()
        self.text = email.mime.text.MIMEText(MSG.format(token = token))
        self.msg.attach(self.text)
        # add headers required
        self.msg['Subject'] = 'MailMonitorFramework: {}'.format(token)
        self.msg['X-MMF-TOKEN'] = token.val()
        self.msg['Message-Id'] = email.utils.make_msgid(token.val())
        self.msg['Date'] = email.utils.formatdate()
        # add headers optional
        if 'mail_from' in config:
            self.msg['From'] = config['mail_from']
        if 'mail_to' in config:
            self.msg['To'] = config['mail_to']
        # add big size mail
        if 'mail_size' in config and config['mail_size'] != "":
            self.size(config['mail_size'])
        # add custom header
        if 'mail_header' in config:
            for hdr in config['mail_header'].split():
                hdr_name = 'mail_header_{}_name'.format(hdr)
                hdr_value = 'mail_header_{}_value'.format(hdr)
                if hdr_name in config and hdr_value in config:
                    value =  '\n\t'.join(config[hdr_value].split('\n'))
                    self.msg.add_header(config[hdr_name], value)
        # add attach file
        if 'mail_attach' in config:
            for attach in config['mail_attach'].split():
                self.attach_file(attach)

    # attach a file in mail
    def attach_file(self, path, name = None):
        # open and read file
        with open(path, 'rb') as fp:
            msg = email.mime.base.MIMEBase('application', 'octet-stream')
            msg.set_payload(fp.read())
            # Encode the payload using Base64
            email.encoders.encode_base64(msg)
        if name is None:
            name = os.path.basename(path)
        # add filename
        msg.add_header('Content-Disposition', 'attachment', filename=name)
        # attach to message
        self.msg.attach(msg)

    def size(self, s, name = 'zero'):
        # size will grow up with base64
        s = s // 4 * 3
        msg = email.mime.base.MIMEBase('application', 'octet-stream')
        msg.set_payload(bytearray(s))
        # encode to base64
        email.encoders.encode_base64(msg)
        # add filename
        msg.add_header('Content-Disposition', 'attachment', filename=name)
        # attach to message
        self.msg.attach(msg)

    def __getitem__(self, key):
        # for convenience use
        return self.msg[key]

    def __setitem__(self, key, value):
        # for convenience use
        self.msg[key] = value

    def __repr__(self):
        # for convenience use
        return self.msg.as_string()

    def as_string(self):
        # for convenience use
        return self.msg.as_string()

    @staticmethod
    def from_str(s):
        # init mail parser
        parser = email.parser.Parser()
        # parse text to email
        mail = parser.parsestr(s)
        return mail

    @staticmethod
    def isbounce(mail):
        # init value
        reason = None
        # if this is a bounce mail
        if mail.get_content_type() == "multipart/report":
            # find delivery-status -> bounce reason(Diagnostic-Code)
            for part in mail.walk():
                if part.get_content_type() == "message/delivery-status":
                    p = part.get_payload()[1]
                    reason = p['Diagnostic-Code']
        # change multi-lines to single line
        if reason is not None:
            reason = ' '.join(reason.split())
        return reason
