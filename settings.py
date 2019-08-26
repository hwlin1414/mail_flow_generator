import os
import configparser

PATH_DEFAULT = os.path.dirname(os.path.abspath(__file__)) + '/mfg.conf'
DEFAULT = {
    'method': 'general',
    'send': 'smtp',
    'recv': 'ipc',
    'anal': '',
    'err': '',
    'loop': '1',
    'socket_timeout': '10',
    'socket_path': '/tmp/',
    'timeout': '120',
    'interval': '60',
    'mail_from': 'mmf@localhost',
    'mail_to': 'mmf@localhost',
    'smtp_protocol': 'smtp',
    'smtp_host': 'localhost',
    'smtp_user': '',
    'smtp_password': '',
    'err_threshold': '1',
}

def case_check(case):
    # Set Default
    if 'smtp_sender' not in case or case['smtp_sender'] == "":
        case['smtp_sender'] = case['mail_from']
    if 'smtp_recipients' not in case or case['smtp_recipients'] == "":
        case['smtp_recipients'] = case['mail_to']

    # Change Type to boolean
    if 'smtp_starttls' in case and case['smtp_starttls'] != "":
        case['smtp_starttls'] = True
    if case['smtp_user'] == "": case['smtp_user'] = False
    if case['smtp_password'] == "": case['smtp_password'] = False

    # Change Type to int
    case['timeout'] = int(case['timeout'])
    case['interval'] = float(case['interval'])
    case['loop'] = int(case['loop'])
    case['socket_timeout'] = int(case['socket_timeout'])
    if 'mail_size' in case: case['mail_size'] = int(case['mail_size'])
    if 'err_threshold' in case: case['err_threshold'] = int(case['err_threshold'])

    # Change Type to List
    case['smtp_recipients'] = [ x.strip() for x in case['smtp_recipients'].split(',') ]
    if 'err_recipients' in case:
        case['err_recipients'] = [ x.strip() for x in case['err_recipients'].split(',') ]

def read(path = PATH_DEFAULT):
    parser = configparser.ConfigParser()
    path2 = "{}.secret".format(path)
    parser.read([path, path2])

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

