import email
import email.mime
import email.mime.text
import email.utils
import email.parser

MSG = """
This is an email generated from Mail Monitor Framework
token: {token}
if you always see this email, please contact mailta@cs.nctu.edu.tw
"""

class Mail():
    def __init__(self, name, token, **kwargs):
        self.msg = email.mime.text.MIMEText(MSG.format(token = token))
        self.msg['Subject'] = 'MailMonitorFramework: {name}/{token}'.format(name = name, token = token)
        self.msg['X-MMF-TOKEN'] = token
        self.msg['Message-Id'] = email.utils.make_msgid(token)
        self.msg['Date'] = email.utils.formatdate()
        if 'from' in kwargs: self.msg['From'] = kwargs['from']
        if 'to' in kwargs: self.msg['To'] = kwargs['to']

    def __getitem__(self,key):
        return self.msg[key]

    def __setitem__(self,key,value):
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
