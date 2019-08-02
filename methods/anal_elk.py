import sys
import re
import urllib.request
import json
import datetime
import time

re_queueid = re.compile('.*queued as (\w+).*')

def query(qid):
    date = datetime.datetime.strftime(datetime.datetime.now(), '%Y.%m.%d')
    url = 'http://{host}:{port}/{index}-{date}/_search'.format(
        host = '10.1.2.101', port = 9200,
        index = 'maillog-postfix', date = date
    )

    request = urllib.request.Request(url, headers = {'Content-Type': 'application/json'})
    request.data = json.dumps({
        "query": {
            "bool": {
                "must": [
                    {"match": {"postfix_queueid": qid}},
                    #{"range": {
                    #    "@timestamp" : {"gte": "now-100m", "lte": "now"}
                    #}}
                ]
            }
        }
    }).encode('UTF-8')

    response = urllib.request.urlopen(request)
    response = response.read().decode('UTF-8')
    data = json.loads(response)
    return data['hits']['hits']

def anal(runtime, config, msg):
    waittimes = 10
    while runtime['ThreadStopFlag'] is False:
        if waittimes == 0: break
        time.sleep(runtime['CheckFlagPeriod'])
        waittimes -= 1

    print("=== elk: {} ===".format(config['token']))
    send_result = config['send_result'][1].decode('UTF-8')
    qid = re_queueid.findall(send_result)
    while True:
        if qid is None or len(qid) == 0: break
        logs = query(qid[0])
        qid = []
        for log in logs:
            temp_qid = re_queueid.findall(json.dumps(log))
            if len(temp_qid) > 0: qid = temp_qid
            print("\t{}".format(log['_source']['message']))


if __name__ == "__main__":
    anal({}, {'send_result': (250, b'2.0.0 Ok: queued as 74D1B2D53D8', {}), }, '')
