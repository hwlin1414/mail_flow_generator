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

class Token():
    def __init__(self, name, **kwargs):
        self.name = name
        self.token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    def val(self):
        return self.token
    def __str__(self):
        return "{}/{}".format(self.name, self.token)

class Mail():
    def __init__(self, name, token, **kwargs):
        self.msg = email.mime.multipart.MIMEMultipart()
        self.text = email.mime.text.MIMEText(MSG.format(token = token))
        self.msg.attach(self.text)
        self.msg['Subject'] = 'MailMonitorFramework: {}'.format(token)
        self.msg['X-MMF-TOKEN'] = token.val()
        self.msg['Message-Id'] = email.utils.make_msgid(token.val())
        self.msg['Date'] = email.utils.formatdate()
        if 'from' in kwargs: self.msg['From'] = kwargs['from']
        if 'to' in kwargs: self.msg['To'] = kwargs['to']
        if 'size' in kwargs and kwargs['size'] != "": self.size(kwargs['size'])

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
