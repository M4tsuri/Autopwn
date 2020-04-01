# coding=utf-8
from pwnlib.util.proc import wait_for_debugger
import sys
import re
import autopwn.core.classes
from pwn import *
import autopwn.ctf.less_tube

# ida: use ida as debugger
# gdb: use gdb as debugger
# 

class Attack(autopwn.core.classes.Autopwn):
    # directly pass argv when you call it, and use out special function
    def __init__(self, argv, config):
        autopwn.core.classes.Autopwn.__init__(self)
        self.mode = argv[1]
        self.log = 'debug'
        self.config = config
        self.execute = 0
        self.server = 0
        self.elf = ELF(config['elf'])
    
    # 启动进程
    def process_init(self):
        context.arch = self.elf.get_machine_arch()
        context.log_level = self.log
        if self.mode == 'ida' or self.mode == 'run' or self.mode == 'gdb':
            if not os.path.exists(self.config['elf']):
                print("ELF file does not exist.")
                exit(1)

            self.execute = process(['./' + self.config['elf']])

            if self.mode == 'ida':
                wait_for_debugger(self.execute.pid)
            elif self.mode == 'gdb':
                gdb.attach(self.execute)

        elif self.mode == 'remote':
            self.server = autopwn.core.classes.Server(self.config['server'], self.config['server_class'])
            try:
                self.execute = self.server.connect()
            except exception.PwnlibException:
                print("Remote server error.")

        else:
            print("Parameter Error.")

        self.execute = autopwn.ctf.less_tube.add_features(self.execute)
        return self.execute
