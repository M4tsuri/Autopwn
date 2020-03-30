# coding=utf-8
from pwnlib.util.proc import wait_for_debugger
import sys
import re
import os
import yaml

# 0 represents debug
# 1 represents process
# 2 represents remote
class Autopwn:
    # directly pass argv when you call it, and use out special function
    def __init__(self, argv, conf_file):
        self.mode = int(argv[1])
        self.elf_file = ''
        self.server_name = ''
        self.server_class = ''
        self.config_init(conf_file)
        self.execute = 0
        self.server = 0
        self.process_init()
        self.elf = ''
        self.get_info()

    # 初始化配置文件
    def config_init(self, conf_file):
        with open(conf_file, 'r') as cf:
            conf = yaml.load(cf, Loader=yaml.BaseLoader)

        self.elf_file = conf['FILE_NAME']
        self.server_name = conf['SERVER_ADDR']
        self.server_class = conf['SERVER_CLASS']

    # 启动进程
    def process_init(self):
        if self.mode == 0 or self.mode == 1:
            if not os.path.exists(self.elf_file):
                print("ELF file does not exist.")
                exit()
            else:
                self.execute = process(['./' + self.elf_file])
            if self.mode == 0:
                wait_for_debugger(self.execute.pid)
        elif self.mode == 2:
            self.server = RemoteServer(self.server_name, self.server_class)
            try:
                self.execute = self.server.connect()
            except exception.PwnlibException:
                print("Remote server error.")
        else:
            print("Parameter Error.")

    def get_info(self):
        self.elf = ELF(self.elf_file)


class RemoteServer:
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


