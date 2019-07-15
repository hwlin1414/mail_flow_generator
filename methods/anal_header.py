import sys
import re

import mail
import email
import email.utils

re_by = re.compile('.*by (\S+).*')
re_id = re.compile('.*\sid (\w+).*')
re_time = re.compile('((?:Sun|Mon|Tue|Wed|Thr|Fri|Sat).*)')

def anal(runtime, config, msg):
    if isinstance(msg, str):
        msg = mail.Mail.from_str(msg)
    recieveds = msg.get_all('Received')

    path = []
    for received in recieveds[::-1]:
        tags = []
        by = re_by.findall(received)[0]
        id = re_id.findall(received)[0]
        time = re_time.findall(received)
        if 'Postfix' in received: tags.append('Postfix')
        if 'from userid' in received: tags.append('LocalUser')
        if 'amavisd-new' in received: tags.append('Amavisd')
        if len(time) > 0:
            time = email.utils.parsedate_to_datetime(time[0])
        path.append({'host': by, 'id': id, 'time': str(time), 'tags': tags})
    print("=== {} ===".format(config['token']))
    for p in path:
        print("\tby: {host} ({id}) time: {time} tags: {tags}".format(**p))

if __name__ == "__main__":
    mailtext = ''.join(sys.stdin.readlines())
    anal({}, {'token': 'stdin'}, mailtext)
