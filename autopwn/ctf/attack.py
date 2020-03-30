# coding=utf-8
from pwnlib.util.proc import wait_for_debugger
import sys
import re
import autopwn.core.classes
from pwn import *

# 0 represents debug
# 1 represents run
# 2 represents remote

class Attack(autopwn.core.classes.Autopwn):
    # directly pass argv when you call it, and use out special function
    def __init__(self, argv, config):
        autopwn.core.classes.Autopwn.__init__(self)
        self.mode = argv[1]
        self.config = config
        self.execute = 0
        self.server = 0
        self.elf = ELF(config['elf'])
    
    # 启动进程
    def process_init(self):
        context.arch = self.config['arch']
        context.log_level = 'debug'
        if self.mode == 'debug' or self.mode == 'run':
            if not os.path.exists(self.config['elf']):
                print("ELF file does not exist.")
                exit(1)

            self.execute = process(['./' + self.config['elf']])

            if self.mode == 'debug':
                wait_for_debugger(self.execute.pid)

        elif self.mode == 'remote':
            self.server = autopwn.Server(self.config['server'], self.config['class'])
            try:
                self.execute = self.server.connect()
            except exception.PwnlibException:
                print("Remote server error.")

        else:
            print("Parameter Error.")

        return self.execute
