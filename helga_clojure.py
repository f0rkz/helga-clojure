import os.path

from subprocess import Popen, PIPE
from threading import Thread

from helga import log
from helga.plugins import command


__all__ = ['clojure']

logger = log.getLogger(__name__)

CLOJURE_JAR = os.path.join(os.path.dirname(__file__), 'lib', 'clojure-1.8.0.jar')
DEFAULT_TIMEOUT_IN_SECONDS = 30


class Clojure(object):

    def __init__(self, code):
        self.code = code
        self.process = None
        self.stdout = ''
        self.stderr = ''

    def run(self, timeout_sec=DEFAULT_TIMEOUT_IN_SECONDS):
        def target():
            self.process = Popen(['java', '-jar', CLOJURE_JAR, '-e', self.code], stdout=PIPE, stderr=PIPE)
            self.stdout, self.stderr = self.process.communicate()

        thread = Thread(target=target)
        thread.start()
        thread.join(timeout_sec)
        if thread.is_alive():
            logger.info('terminating thread: [[%s]]', self.code)
            self.process.terminate()
            thread.join()
            self.stderr = 'subprocess timed out after {} seconds'.format(timeout_sec)

        return self.process.returncode, self.stdout.strip(), self.stderr.strip()


def excerpt(string):
    return string[:string.find('\n')] if '\n' in string else string


@command('clojure', aliases=['clj'],
         help='Run Clojure expressions. Usage: helga clojure <expression>')
def clojure(client, channel, nick, message, cmd, args):
    if not args:
        return '{}, how about some code to go with that?'.format(nick)

    code = ' '.join(args)
    logger.debug('running: %s', code)

    try:
        exit_code, stdout, stderr = Clojure(code).run()
    except Exception as e:
        logger.exception('caught exception while running [[%s]]', code)
        return 'caught exception: {}'.format(str(e))
    else:
        if exit_code == 0:
            return stdout
        else:
            logger.warning('subprocess returned %d for [[%s]], stderr follows:\n%s', exit_code, code, stderr)
            return 'error ({}): {}'.format(exit_code, excerpt(stderr))
