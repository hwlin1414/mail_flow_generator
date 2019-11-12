import sys
import re

import mail
import email
import email.utils

# header pattern matching
re_by = re.compile('.*by (\S+).*')
re_id = re.compile('.*\sid (\w+).*')
re_time = re.compile('((?:Sun|Mon|Tue|Wed|Thr|Fri|Sat).*)')

# analysis module
def analysis(runtime, config):
    # return if no mail in config
    if 'mail_msg_recv' not in config: return
    msg = config['mail_msg_recv']
    # parse text to mail
    if isinstance(msg, str):
        msg = mail.Mail.from_str(msg)
    recieveds = msg.get_all('Received')

    # crawl mail and parse pattern
    path = []
    for received in recieveds[::-1]:
        tags = []
        try:
            # find mail receive by who
            tmp_by = re_by.findall(received)
            by = tmp_by[0] if len(tmp_by) > 0 else ''
            # find mail receive queue-id
            tmp_id = re_id.findall(received)
            id = tmp_id[0] if len(tmp_id) > 0 else ''
            # find mail receive time
            time = re_time.findall(received)
            # if specifice flag in header
            if 'Postfix' in received: tags.append('Postfix')
            if 'from userid' in received: tags.append('LocalUser')
            if 'amavisd-new' in received: tags.append('Amavisd')
            # check if important data parsed
            if len(time) > 0:
                time = email.utils.parsedate_to_datetime(time[0])
            # append data to path
            path.append({'host': by, 'id': id, 'time': str(time), 'tags': tags})
        except:
            pass
    # print out message path
    print("=== header: {} ===".format(config['token']))
    for p in path:
        print("\tby: {host} ({id}) time: {time} tags: {tags}".format(**p))

if __name__ == "__main__":
    # stdin mail
    mailtext = ''.join(sys.stdin.readlines())
    analysis({}, {'token': 'stdin'}, mailtext)
