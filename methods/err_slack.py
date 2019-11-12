import json
import urllib.request

def slack_msg(channel, message, detail, isalert = False):
    # slack username
    username = 'MailMon'
    # slack url
    url = 'https://hooks.slack.com/services/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'
    # slack bot image
    img = 'wink'
    color = '36a64f'
    detail_title = 'Alert'

    # is alert, change color to read
    if isalert is True:
        img = 'sweat'
        color = 'D00000'

    # create api payload
    payload = {
        "channel": "#{}".format(channel),
        "username": "{}".format(username),
        "attachments": [{
            "fallback": "Required plain-text summary of the attachment.",
            "color": "#{}".format(color),
            "pretext": "{}".format(message),
            "fields": [{
                "title": "{}".format(detail_title),
                "value": "{}".format(detail),
                "short": 'false',
            }],
        }],
        "icon_emoji": ":{}:".format(img),
    }
    data = json.dumps(payload)
    # try send message to slack in http
    try:
        req = urllib.request.Request(
            url,
            data=data.encode('UTF-8'),
            headers={'Content-Type': 'application/json'}
        )
        # read response
        resp = urllib.request.urlopen(req)
    except Exception as em:
        print('Exception: {}'.format(em))

def err(runtime, config):
    # if error not in config , return
    if 'errors' not in config or len(config['errors']) == 0: return

    # prepare error message
    errtitle = 'Mail Error {}'.format(config['token'])
    errmsg = ''
    for x in config['errors']:
        errmsg += 'Unexpected error {}: {}\n'.format(type(x), x)
    # send error message
    slack_msg(config['slack_channel'], errtitle, errmsg, isalert = True)

if __name__ == "__main__":
    #slack_msg('machine-log', 'test', 'test err_slack.py', isalert = True)
    pass
