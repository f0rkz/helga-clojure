import os.path

from subprocess import Popen

from helga.plugins import command


CLOJURE_JAR = os.path.join(os.path.dirname(__file__), 'lib', 'clojure-1.8.0.jar')


@command('clojure', aliases=['clj'],
         help='')   # TODO
def clojure(client, channel, nick, message, cmd, args):
    try:
        java = Popen(['java', '-jar', CLOJURE_JAR, '-e', ' '.join(args)])
        java.wait()
        if java.returncode == 0:
            return java.stdout
        else:
            return 'subprocess returned {}, stderr follows: {}'.format(java.returncode, java.stderr)
    except Exception as e:
        return 'caught exception: {}'.format(str(e))
