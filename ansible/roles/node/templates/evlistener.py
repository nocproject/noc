#!/opt/noc/bin/python

# from https://github.com/alerta/alerta-contrib/tree/master/integrations/supervisor

import sys
import json
import platform

from alerta.api import ApiClient
from alerta.alert import Alert
from alerta.heartbeat import Heartbeat


class Listener(object):

    def wait(self):

        data = sys.stdin.readline()
        headers = dict([x.split(':') for x in data.split()])
        data = sys.stdin.read(int(headers['len']))
        body = dict([x.split(':') for x in data.split()])
        return headers, body

    def send_cmd(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def log_stderr(self, s):
        sys.stderr.write(s)
        sys.stderr.flush()


def main():

    api = ApiClient()
    listener = Listener()

    while True:
        listener.send_cmd('READY\n')
        headers, body = listener.wait()

        event = headers['eventname']
        if event.startswith('TICK'):
            supervisorAlert = Heartbeat(
                origin=headers['server'],
                timeout=124,
                tags=[headers['ver'], event]
            )
        try:
            api.send(supervisorAlert)
        except Exception as e:
            listener.log_stderr(e)
            listener.send_cmd('RESULT 4\nFAIL')
        else:
            listener.send_cmd('RESULT 2\nOK')

if __name__ == '__main__':
    main()