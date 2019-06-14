import sys
import copy
import datetime
import importlib
import threading
import time
import traceback

# function run to start all manager and wait them all.
def run(runtime):
    # remember all manager threads
    ManagerThreads = []
    # create manager threads
    for case in runtime['config']['cases']:
        thr = Manager(runtime, runtime['config']['cases'][case])
        thr.start()
        ManagerThreads.append(thr)
    # wait manager threads to stop
    for thr in ManagerThreads:
        thr.join()
    # invalidate python cache files(for reload modules)
    importlib.invalidate_caches()

class Manager(threading.Thread):
    def __init__(self, runtime, config, *args, **kwargs):
        threading.Thread.__init__(self, name = config['name'], *args, **kwargs)
        self._runtime = runtime
        self._config = config

    def run(self):
        runtime = self._runtime
        config = self._config
        runtime['log'].debug("Manager {} Start".format(config['name']))

        # first load module and reload module
        try:
            # load module(when first execute this line)
            method = importlib.import_module('methods.{}'.format(config['method']))
            # reload module(to ensure load new module when programmer change code)
            method = importlib.reload(method)
        except ImportError as msg:
            runtime['log'].error(msg)
            return
        # initial variables
        counter = 0
        interval = datetime.timedelta(seconds = config['interval'])
        # manager started at
        start = datetime.datetime.now().replace(microsecond = 0)
        # next generator start
        nextstart = start
        # remember all manager threads
        GeneratorThreads = []
        # while thread not stop, loop
        while runtime['ThreadStopFlag'] is False:
            now = datetime.datetime.now().replace(microsecond = 0)
            # if nextstart time's up
            if now >= nextstart:
                # copy new config to avoid changing by threads
                conf = copy.deepcopy(config)
                # add counter to config
                conf['threadnum'] = counter
                # thread start
                thr = Generator(runtime, conf, method)
                thr.start()
                GeneratorThreads.append(thr)

                # calc next start time
                nextstart = now + interval
                # increase counter
                counter += 1
                # check if need exit that counter reach loop times
                if config['loop'] != -1 and counter >= config['loop']:
                    break
            else:
                time.sleep(runtime['CheckFlagPeriod'])

        # recieve thread stop flag or counter reach loop times, need cleanup
        for thr in GeneratorThreads:
            thr.join()
        runtime['log'].debug("Manager {} Stop".format(config['name']))

class Generator(threading.Thread):
    def __init__(self, runtime, config, method, *args, **kwargs):
        name = "{}-{}".format(config['name'], config['threadnum'])
        threading.Thread.__init__(self, name = name, *args, **kwargs)
        self._runtime = runtime
        self._config = config
        self._method = method

    def run(self):
        runtime = self._runtime
        config = self._config
        method = self._method

        runtime['log'].debug("Generator Start")

        try:
            # get function 'run' in user defined module
            function = getattr(method, 'run')
            # run the function
            function(runtime, config)
        # except for all unexpected error and log
        except:
            err = sys.exc_info()
            runtime['log'].error('Unexpected error {}:{}, tb: {}'.format(
                err[0],
                err[1],
                ','.join(traceback.format_tb(err[2]))
            ))

        runtime['log'].debug("Generator Stop")
