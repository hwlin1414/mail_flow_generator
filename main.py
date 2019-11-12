import os
import argparse
import signal
import threading

import logger
import settings
import workload

# Application name in Log
appname = 'MailFlowGenerator'
# log instance, we need to log something in signal handler
log = logger.logger(appname, os.path.dirname(os.path.abspath(__file__)) + '/app.log')
# global variable
runtime = {
    'log': log,
    # stop all threads
    'ThreadStopFlag': False,
    # stop program
    'ProgramStopFlag': False,
    # all thread check flags in period
    'CheckFlagPeriod': 1,
    'config': {},
    'threaddata': {},
}

# reload program
def reload(signum, stack_frame):
    log.warning('signal {} recieved, reload'.format(signum))
    runtime['ThreadStopFlag'] = True

# stop program
def shutdown(signum, stack_frame):
    log.warning('signal {} recieved, shutdown'.format(signum))
    runtime['ThreadStopFlag'] = True
    runtime['ProgramStopFlag'] = True

def main(config_path, debug):
    runtime['log'].info("Program start")

    if debug == True:
        logger.setdebug(runtime['log'])

    # bind handlers to signal number
    signal.signal(signal.SIGHUP, reload)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # while program not stop, loop when reload
    while runtime['ProgramStopFlag'] is False:
        # reset flags which tell all thread to stop
        runtime['ThreadStopFlag'] = False
        # reload config file
        runtime['config'] = settings.read(config_path)
        # run workload
        workload.run(runtime)
        # if workload exit normally(not by reload signal), break the loop
        if runtime['ThreadStopFlag'] is False:
            break

    runtime['log'].info("Program exited")

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description = '{}'.format(appname))
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
    parser.add_argument('-c', '--config', default=settings.PATH_DEFAULT, help='Config file path')
    args = parser.parse_args()

    # Run main program
    main(args.config, args.debug)
