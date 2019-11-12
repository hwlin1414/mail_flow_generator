import sys

# deprecated module
def err(runtime, config):
    # if error not in config, return
    if 'errors' not in config or len(config['errors']) == 0: return
    # for each error message
    for err in config['errors']:
        # parse error message
        errtitle = 'Unexpected error {}'.format(type(err))
        errmsg = str(err)
        # printout error message
        runtime['log'].error('{}: {}'.format(errtitle, errmsg))
