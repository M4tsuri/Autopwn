class Autopwn:
    def __init__(self):
        self.flag_pattern = re.compile(flag_pattern)
        pass

    def exp(self):
        pass

    def get_flag(self):
        pass

class Server:
    def __init__(self, server_name, server_class):
        self.server_name = server_name
        self.method = server_class

    # 解析nc连接地址及端口
    def _nc_parse(self):
        res = {
            'host': '',
            'port': 0
        }
        self.server_name = self.server_name.split(':')
        res['host'] = self.server_name[0]
        res['port'] = int(self.server_name[1])
        return res

    # ssh格式为用户名:地址:密码:端口
    def _ssh_parse(self):
        res = {
            'username': '',
            'host': '',
            'passwd': '',
            'port': 21,
        }
        self.server_name = self.server_name.split(':')
        res['username'] = self.server_name[0]
        res['host'] = self.server_name[1]
        res['passwd'] = self.server_name[2]
        if len(self.server_name) == 4:
            res['port'] = int(self.server_name[3])
        return res

    def _nc_connect(self, nc_args):
        try:
            return remote(nc_args['host'], nc_args['port'])
        except:
            print("Connention to netcat failed.")
            exit(1)

    def _ssh_connect(self, ssh_args):
        try:
            return ssh(ssh_args['username'], ssh_args['host'], ssh_args['port'], ssh_args['passwd'])
        except:
            print("Connection to ssh failed")
            exit(1)

    def connect(self):
        if self.method == 'nc':
            return self._nc_connect(self._nc_parse())
        elif self.method == 'ssh':
            return self._ssh_connect(self._ssh_parse())
        else:
            return None