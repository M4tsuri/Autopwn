# coding=utf-8
from pwnlib.util.proc import wait_for_debugger
import sys
import re
import autopwn.core.classes
import autopwn.ctf.less_tube
import lief
from pwn import *
from pathlib import Path

# ida: use ida as debugger
# gdb: use gdb as debugger
# run: run with local elf file
# remote: attack remote server

class Attack(autopwn.core.classes.Autopwn):
    # directly pass argv when you call it, and use out special function
    def __init__(self, argv: list, config: dict, inter=None, needed=None):
        self.mode = argv[1]
        self.log_level = 'debug'
        self.config: dict = config
        # basic configuration

        self.gdbscript = '''
                b main
                continue
                '''
        context.terminal = ['terminator', '-e']
        # debugger configuration

        self.execute: pwnlib.tubes.sock.sock = None
        # our process to interact
        self.server: autopwn.core.classes.Server = None
        # the server to be connected when using remote mode

        self.work_path = Path(argv[0]).parent
        self.elf_path = Path(config['elf']).absolute()
        self.elf = ELF(str(self.elf_path))

        self.inter_modified = bool(inter != None)
        self.needed_modified = bool(needed != None)

        if self.needed_modified:
            self.needed_path = [Path(lib).absolute() for lib in needed]
            self.lib = [ELF(str(lib_path)) for lib_path in self.needed_path]
        if self.inter_modified:
            self.inter_path = Path(inter).absolute()
            self.inter: pwnlib.elf.ELF = ELF(str(self.inter_path))
        
        self.parsed: lief.Binary = None
        # extend lief support


    def parse(self):
        self.parsed = lief.parse(self.elf_path)
        assert type(self.parsed) == lief.Binary
        return self.parsed


    def ensurelib(self):
        if type(self.parsed) != lief.Binary:
            self.parse()
    
        exit_value = 0
        if self.inter_modified:
            command = f"patchelf --set-interpreter {str(self.inter_path)} {str(self.elf_path)}"
            log_level.info("Executing: " + command)
            exit_value = os.system(command)
        
        if self.needed_path:
            needed = []
            for replace in self.needed_path:
                needed.append(self.parse_path(replace))
            #print needed
            
            lib_pattern = re.compile(r"lib[a-zA-Z]+")
            for origin in self.parsed.libraries:
                for replace in needed:
                    self.lib.append(ELF(replace[0]))
                    #print re.findall(lib_pattern, origin)[0]
                    if re.findall(lib_pattern, replace[1])[0] in origin:
                        command = "patchelf --replace-needed {} {} {}".format(origin, replace[0], elf)
                        log_level.info("Executing: " + command)
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
        context.log_level = self.log_level
        if self.mode == 'ida' or self.mode == 'run' or self.mode == 'gdb':
            if not self.elf_path.exists():
                log_level.error("ELF file does not exist.")
                exit(1)

            if self.mode == 'gdb':
                self.execute = gdb.debug([str(self.elf_path)], self.gdbscript)
            else:
                self.execute = process([str(self.elf_path)])
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
