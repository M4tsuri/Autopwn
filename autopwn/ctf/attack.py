# coding=utf-8
from pwnlib.util.proc import wait_for_debugger
import sys
import re
import autopwn.core.classes
import autopwn.ctf.less_tube
import lief
import os
from pwn import *

# ida: use ida as debugger
# gdb: use gdb as debugger
# 

class Attack(autopwn.core.classes.Autopwn):
    # directly pass argv when you call it, and use out special function
    def __init__(self, argv, config, inter, needed):
        self.mode = argv[1]
        self.log = 'debug'
        self.config = config
        self.execute = 0
        self.server = 0
        self.elf = ELF(config['elf'])

        self.gdbscript = '''
                b main
                continue
                '''
        context.terminal = ['terminator', '-e']

        self.parsed = 0
        self.ensured = False
        if needed:
            self.lib = [ELF(os.path.abspath(lib)) for lib in needed]
        if inter:
            self.lib.append(ELF("./" + inter))
        self.needed = needed
        self.inter = inter
        self.realpath = os.path.abspath(argv[0])[:-(len(argv[0]))]

    def parse(self):
        self.parsed = lief.parse('./' + self.config['elf'])
        assert type(self.parsed) != type(0)
        return self.parsed

    # path[0] is absolute path
    # path[1] is dirtionary
    # path[2] is file name
    @staticmethod
    def parse_path(path):
        res = []
        res.append(os.path.abspath(path))
        res.append(os.path.basename(path))
        return res

    def ensurelib(self):
        if self.ensured:
            return

        if not self.parsed:
            self.parse()

        elf = self.realpath + self.config['elf']
        exit_value = 0
        if self.inter:
            inter = self.parse_path(self.inter)
            command = "patchelf --set-interpreter {} {}".format(inter[0], elf)
            log.info("Executing: " + command)
            exit_value = os.system(command)
        
        if self.needed:
            needed = []
            for replace in self.needed:
                needed.append(self.parse_path(replace))
            #print needed
            
            lib_pattern = re.compile(r"lib[a-zA-Z]+")
            for origin in self.parsed.libraries:
                for replace in needed:
                    self.lib.append(ELF(replace[0]))
                    #print re.findall(lib_pattern, origin)[0]
                    if re.findall(lib_pattern, replace[1])[0] in origin:
                        command = "patchelf --replace-needed {} {} {}".format(origin, replace[0], elf)
                        log.info("Executing: " + command)
                        exit_value += os.system(command)

        self.elf = ELF(self.config['elf'])
        self.ensured = True
        return exit_value

    def breakat(self, breakpoint):
        if self.elf.pie:
            self.gdbscript = '''
                    b *$rebase({})
                    continue
                    '''.format(hex(breakpoint))
        else:
            self.gdbscript = '''
                    b *{}
                    continue
                    '''.format(hex(breakpoint))
    
    # 启动进程
    def process_init(self):
        context.arch = self.elf.get_machine_arch()
        context.log_level = self.log
        if self.mode == 'ida' or self.mode == 'run' or self.mode == 'gdb':
            if not os.path.exists(self.config['elf']):
                log.error("ELF file does not exist.")
                exit(1)

            if self.mode == 'gdb':
                self.execute = gdb.debug(['./' + self.config['elf']], self.gdbscript)
            else:
                self.execute = process(['./' + self.config['elf']])
            if self.mode == 'ida':
                wait_for_debugger(self.execute.pid)

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
