import sys

def err(runtime, config):
    if 'errors' not in config or len(config['errors']) == 0: return
    for err in config['errors']:
        errtitle = 'Unexpected error {}'.format(type(err))
        errmsg = str(err)
        runtime['log'].error('{}: {}'.format(errtitle, errmsg))
