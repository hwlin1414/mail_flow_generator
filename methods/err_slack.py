import json
import urllib.request

def slack_msg(channel, message, detail, isalert = False):
    username = 'MailMon'
    url = 'https://hooks.slack.com/services/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'
    img = 'wink'
    color = '36a64f'
    detail_title = 'Alert'

    if isalert is True:
        img = 'sweat'
        color = 'D00000'

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
    print(data)
    try:
        req = urllib.request.Request(
            url,
            data=data.encode('UTF-8'),
            headers={'Content-Type': 'application/json'}
        )
        resp = urllib.request.urlopen(req)
    except Exception as em:
        print('Exception: {}'.format(em))

def err(runtime, config):
    pass
    errtitle = 'Mailmon Error {}'.format(config['token'])
    errmsg = ''
    slack_msg(config['slack_channel'], errtitle, errmsg)

if __name__ == "__main__":
    #slack_msg('machine-log', 'test', 'test err_slack.py')
    pass
