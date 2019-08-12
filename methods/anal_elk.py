import sys
import re
import urllib.request
import json
import datetime
import time

DEF_ELK_WAIT = 10
re_queueid = re.compile('.*queued as (\w+).*')

def query(config, qid = None, host = None, mid = None):
    date = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y.%m.%d')
    port = config['elk_port'] if 'elk_port' in config else 9200
    url = 'http://{host}:{port}/{index}-{date}/_search'.format(
        host = config['elk_host'], port = port,
        index = config['elk_index'], date = date
    )

    request = urllib.request.Request(url, headers = {'Content-Type': 'application/json'})
    filt = []
    if qid is not None: filt.append({'match': {'postfix_queueid': qid}})
    if host is not None: filt.append({'match': {'logsource': host}})
    if mid is not None: filt.append({'match': {'postfix_message-id': mid}})
    #filt = [
    #    {"match": {"postfix_queueid": qid}},
    #    {"match": {"logsource": host}},
    #    {"range": {
    #        "@timestamp" : {"gte": "now-100m", "lte": "now"}
    #    }}
    #]
    request.data = json.dumps({
        "query": {
            "bool": {
                "must": [
                    filt
                ]
            }
        }
    }).encode('UTF-8')

    response = urllib.request.urlopen(request)
    response = response.read().decode('UTF-8')
    data = json.loads(response)
    return data['hits']['hits']

def anal(runtime, config):
    waittimes = config['elk_wait'] if 'elk_wait' in config else DEF_ELK_WAIT
    while runtime['ThreadStopFlag'] is False:
        if waittimes == 0: break
        time.sleep(runtime['CheckFlagPeriod'])
        waittimes -= 1

    print("=== elk: {} ===".format(config['token']))
    send_result = config['send_result'][1].decode('UTF-8')
    #qid = re_queueid.findall(send_result)
    qid = []
    if 'elk_path' in config:
        paths = config['elk_path'].split()
        while True:
            if qid is None or len(qid) == 0:
                if len(paths) == 0: break
                try:
                    logs = query(config, host = paths[0], mid = config['mail_msg_send']['Message-Id'])
                    if len(logs) == 0:
                        paths.pop(0)
                        continue
                    print('pop from elk_path')
                    qid = [logs[0]['_source']['postfix_queueid']]
                except urllib.error.HTTPError as err:
                    runtime['log'].error('Unexpected error {}: {}'.format(type(err), str(err)))
            print('trying: qid={}, paths={}'.format(qid, paths))
            try:
                logs = query(config, qid = qid[0])
            except urllib.error.HTTPError as err:
                runtime['log'].error('Unexpected error {}: {}'.format(type(err), str(err)))
                logs = []
            qid = []
            logsource = None
            for log in logs:
                logsource = log['_source']['logsource']
                temp_qid = re_queueid.findall(json.dumps(log))
                if len(temp_qid) > 0: qid = temp_qid
                print("\t{}: {}".format(logsource, log['_source']['message']))
            if len(paths) > 0:
                if logsource == paths[0]:
                    paths.pop(0)
                #else:
                #    print("\telk_path expect: {}, but mail is now {}".format(paths, logsource))
    else:
        while True:
            if qid is None or len(qid) == 0: break
            try:
                logs = query(config, qid = qid[0])
            except urllib.error.HTTPError as err:
                runtime['log'].error('Unexpected error {}: {}'.format(type(err), str(err)))
                logs = []
            qid = []
            for log in logs:
                temp_qid = re_queueid.findall(json.dumps(log))
                if len(temp_qid) > 0: qid = temp_qid
                print("\t{}: {}".format(log['_source']['logsource'], log['_source']['message']))

if __name__ == "__main__":
    anal({}, {'send_result': (250, b'2.0.0 Ok: queued as 74D1B2D53D8', {}), }, '')
