import re

class Autopwn(object):

    def exp(self, a):
        pass

    def get_flag(self, a):
        pass

class Server:
    def __init__(self, server_info, server_class):
        self.ip_port = self._ip_parse(server_info["ip_port"])
        self.username = server_info['username']
        self.password = server_info['password']
        self.method = server_class

    # parse nc address and port
    @staticmethod
    def _ip_parse(ip_port):
        res = {
            'host': '',
            'port': 0
        }
        server_name = ip_port.split(':')
        res['host'] = server_name[0]
        res['port'] = int(server_name[1])
        return res

    def _nc_connect(self):
        from pwnlib.tubes.remote import remote
        try:
            return remote(self.ip_port['host'], self.ip_port['port'])
        except BaseException as e:
            print("Connention to netcat failed: ")
            print e
            exit(1)

    def _ssh_connect(self):
        from pwnlib.tubes.ssh import ssh
        try:
            return ssh(self.username, self.ip_port['host'], self.ip_port['port'], self.password)
        except BaseException as e:
            print("Connection to ssh failed: ")
            print e
            exit(1)

    def connect(self):
        if self.method == 'nc':
            return self._nc_connect()
        elif self.method == 'ssh':
            return self._ssh_connect()
        else:
            return None