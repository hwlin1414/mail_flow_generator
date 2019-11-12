import sys
import re
import urllib.request
import json
import datetime
import time

DEF_ELK_WAIT = 10
# elk log pattern
re_queueid = re.compile('.*queued as (\w+).*')
re_error = re.compile('.*status=(?:deferred|bounced) \((.+)\).*')

def query(config, qid = None, host = None, mid = None):
    # get today date, for compose elk index
    date = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y.%m.%d')
    # elk port
    port = config['elk_port'] if 'elk_port' in config else 9200
    # elk url
    url = 'http://{host}:{port}/{index}-{date}/_search'.format(
        host = config['elk_host'], port = port,
        index = config['elk_index'], date = date
    )

    # elk search request
    request = urllib.request.Request(url, headers = {'Content-Type': 'application/json'})
    filt = []
    # add query filter
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
    # elk query data
    request.data = json.dumps({
        "query": {
            "bool": {
                "must": [
                    filt
                ]
            }
        }
    }).encode('UTF-8')

    # post data to elk
    response = urllib.request.urlopen(request)
    # response change to utf-8
    response = response.read().decode('UTF-8')
    data = json.loads(response)
    # return data response from elk
    return data['hits']['hits']

def analysis(runtime, config):
    # wait for a few seconds for elk handling log
    waittimes = config['elk_wait'] if 'elk_wait' in config else DEF_ELK_WAIT
    while runtime['ThreadStopFlag'] is False:
        # sleep for a while and check flag
        if waittimes == 0: break
        time.sleep(runtime['CheckFlagPeriod'])
        waittimes -= 1

    # output elk query result
    print("=== elk: {} ===".format(config['token']))
    send_result = config['send_result'][1].decode('UTF-8')
    # find queue id in smtp send result
    qid = re_queueid.findall(send_result)
    # if elk path is configured
    if 'elk_path' in config:
        paths = config['elk_path'].split()
        # find queue id until cannot find anymore
        while True:
            # if no queue id in send result
            if qid is None or len(qid) == 0:
                if len(paths) == 0: break
                try:
                    # query log by host and msg id
                    logs = query(config, host = paths[0], mid = config['mail_msg_send']['Message-Id'])
                    if len(logs) == 0:
                        paths.pop(0)
                        continue
                    # find queue id
                    #print('pop from elk_path')
                    qid = [logs[0]['_source']['postfix_queueid']]
                except urllib.error.HTTPError as err:
                    # handle http error
                    runtime['log'].error('Unexpected error {}: {}'.format(type(err), str(err)))
            #print('trying: qid={}, paths={}'.format(qid, paths))
            try:
                # query elk by uid
                logs = query(config, qid = qid[0])
            except urllib.error.HTTPError as err:
                # handle error
                runtime['log'].error('Unexpected error {}: {}'.format(type(err), str(err)))
                logs = []
            # reset and init qid
            qid = []
            logsource = None
            # find logs
            for log in logs:
                # find error message and reason
                err = re_error.findall(log['_source']['message'])
                # append error message into errors
                if len(err) > 0: config['errors'].append(err[0])

                # get logsource to find message
                logsource = log['_source']['logsource']
                # find next queue id to search next raw
                temp_qid = re_queueid.findall(json.dumps(log))
                if len(temp_qid) > 0: qid = temp_qid
                print("\t{}: {}".format(logsource, log['_source']['message']))
            if len(paths) > 0:
                # if no data avaliable, try to find mail in elk_path
                if paths[0] in logsource:
                    paths.pop(0)
                #else:
                #    print("\telk_path expect: {}, but mail is now {}".format(paths, logsource))
    else:
        # if no elk_path exist
        while True:
            if qid is None or len(qid) == 0: break
            try:
                # query log by queue-id
                logs = query(config, qid = qid[0])
            except urllib.error.HTTPError as err:
                # handle http error
                runtime['log'].error('Unexpected error {}: {}'.format(type(err), str(err)))
                logs = []
            qid = []
            # search logs
            for log in logs:
                # find error message and reason
                err = re_error.findall(log['_source']['message'])
                # append error message into errors
                if len(err) > 0: config['errors'].append(err[0])

                # find next queue-id
                temp_qid = re_queueid.findall(json.dumps(log))
                if len(temp_qid) > 0: qid = temp_qid
                if 'logsource' in log['_source']:
                    # printout log messages
                    print("\t{}: {}".format(log['_source']['logsource'], log['_source']['message']))
                else:
                    # some message not contain qid message
                    print("\t{}".format(log['_source']['message']))

if __name__ == "__main__":
    # module test
    analysis({}, {'send_result': (250, b'2.0.0 Ok: queued as 74D1B2D53D8', {}), }, '')
