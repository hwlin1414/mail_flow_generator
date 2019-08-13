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
    def __init__(self, config):
        token = config['token']
        self.msg = email.mime.multipart.MIMEMultipart()
        self.text = email.mime.text.MIMEText(MSG.format(token = token))
        self.msg.attach(self.text)
        self.msg['Subject'] = 'MailMonitorFramework: {}'.format(token)
        self.msg['X-MMF-TOKEN'] = token.val()
        self.msg['Message-Id'] = email.utils.make_msgid(token.val())
        self.msg['Date'] = email.utils.formatdate()
        if 'mail_from' in config:
            self.msg['From'] = config['mail_from']
        if 'mail_to' in config:
            self.msg['To'] = config['mail_to']
        if 'mail_size' in config and config['mail_size'] != "":
            self.size(config['mail_size'])
        if 'mail_header' in config:
            for hdr in config['mail_header'].split():
                hdr_name = 'mail_header_{}_name'.format(hdr)
                hdr_value = 'mail_header_{}_value'.format(hdr)
                if hdr_name in config and hdr_value in config:
                    value =  '\n\t'.join(config[hdr_value].split('\n'))
                    self.msg.add_header(config[hdr_name], value)
        if 'mail_attach' in config:
            for attach in config['mail_attach'].split():
                self.attach_file(attach)

    def attach_file(self, path, name = None):
        with open(path, 'rb') as fp:
            msg = email.mime.base.MIMEBase('application', 'octet-stream')
            msg.set_payload(fp.read())
            # Encode the payload using Base64
            email.encoders.encode_base64(msg)
        if name is None:
            name = os.path.basename(path)
        msg.add_header('Content-Disposition', 'attachment', filename=name)
        self.msg.attach(msg)

    def size(self, s, name = 'zero'):
        # size will grow up with base64
        s = s // 4 * 3
        msg = email.mime.base.MIMEBase('application', 'octet-stream')
        msg.set_payload(bytearray(s))
        email.encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=name)
        self.msg.attach(msg)

    def __getitem__(self, key):
        return self.msg[key]

    def __setitem__(self, key, value):
        self.msg[key] = value

    def __repr__(self):
        return self.msg.as_string()

    def as_string(self):
        return self.msg.as_string()

    @staticmethod
    def from_str(s):
        parser = email.parser.Parser()
        mail = parser.parsestr(s)
        return mail
    @staticmethod
    def isbounce(mail):
        reason = None
        if mail.get_content_type() == "multipart/report":
            for part in mail.walk():
                if part.get_content_type() == "message/delivery-status":
                    p = part.get_payload()[1]
                    reason = p['Diagnostic-Code']
        if reason is not None:
            reason = ' '.join(reason.split())
        return reason
