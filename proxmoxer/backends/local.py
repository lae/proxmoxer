__author__ = 'Musee Ullah'
__copyright__ = '(c) Oleg Butovich 2013-2017'
__licence__ = 'MIT'


from itertools import chain
import json, subprocess, shlex


class Response(object):
    def __init__(self, content, status_code):
        self.status_code = status_code
        self.content = content
        self.headers = {"content-type": "application/json"}


class ProxmoxLocalSession(object):
    def __init__(self, sudo=False):
        self.sudo = sudo

    def _exec(self, cmd):
        if self.sudo:
            cmd = "sudo " + cmd
        prepared_cmd = shlex.split(cmd)
        pipe = subprocess.Popen(prepared_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = pipe.communicate()
        return stdout, stderr

    # noinspection PyUnusedLocal
    def request(self, method, url, data=None, params=None, headers=None):
        method = method.lower()
        data = data or {}
        params = params or {}
        url = url.strip()

        cmd = {'post': 'create',
               'put': 'set'}.get(method, method)

        translated_data = ' '.join(["-{0} {1}".format(k, v) for k, v in chain(data.items(), params.items())])
        full_cmd = 'pvesh {0}'.format(' '.join(filter(None, (cmd, url, translated_data))))

        stdout, stderr = self._exec(full_cmd)
        try:
            status_code = int(stderr.split()[0])
        except:
            status_code = 500
        return Response(stdout, status_code)


class JsonSimpleSerializer(object):

    def loads(self, response):
        try:
            return json.loads(response.content)
        except ValueError:
            return response.content


class Backend(object):
    def __init__(self, sudo=False):
        self.session = ProxmoxLocalSession(sudo=sudo)

    def get_session(self):
        return self.session

    def get_base_url(self):
        return ''

    def get_serializer(self):
        return JsonSimpleSerializer()
