import os
import configparser

PATH_DEFAULT = os.path.dirname(os.path.abspath(__file__)) + '/mfg.conf'
DEFAULT = {
    'method': 'smtp',
    'from': 'mmf@localhost',
    'to': 'mmf@localhost',
    'sender': '',
    'recipients': '',
    'timeout': '20',
    'interval': '5',
    'smtp_protocol': 'smtp',
    'smtp_starttls': '',
    'smtp_host': 'localhost',
    'smtp_user': '',
    'smtp_password': '',
    'notification': '',
    'loop': '-1',
    'socket_timeout': '10',
    'socket_path': '/tmp/',
}

def case_check(case):
    # Change Type to int
    case['timeout'] = int(case['timeout'])
    case['interval'] = int(case['interval'])
    case['loop'] = int(case['loop'])
    case['socket_timeout'] = int(case['socket_timeout'])

    # Change Type to boolean
    if case['smtp_starttls'] != "": case['smtp_starttls'] = True
    if case['smtp_user'] == "": case['smtp_user'] = False
    if case['smtp_password'] == "": case['smtp_password'] = False

    # Set Default
    if case['sender'] == "": case['sender'] = case['from']
    if case['recipients'] == "": case['recipients'] = case['to']

    # Change Type to List
    case['recipients'] = [ x.strip() for x in case['recipients'].split(',') ]
    case['notification'] = [ x.strip() for x in case['notification'].split(',') ]

def read(path = PATH_DEFAULT):
    parser = configparser.ConfigParser()
    parser.read(path)

    config = {'cases': {}}
    config['DEFAULT'] = dict(parser['DEFAULT'])
    for section in parser.sections():
        case = {}
        case.update(DEFAULT)
        case.update(dict(config['DEFAULT']))
        case.update(dict(parser[section]))
        case['name'] = section
        case_check(case)
        config['cases'][section] = case

    return config

