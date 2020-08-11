# coding=utf-8
from pwnlib.util.proc import wait_for_debugger
import sys
import re
from autopwn.core.classes import Server
from autopwn.ctf.less_tube import add_features
import lief
from pwn import *
from pathlib import Path
import itertools

# ida: use ida as debugger
# gdb: use gdb as debugger
# run: run with local elf file
# remote: attack remote server

class Attack:
    # directly pass argv when you call it, and use out special function
    def __init__(self, argv: list, config: dict, inter=None, needed=None):
        self.mode = argv[1]
        self.debug_mode = False
        self.log_level = 'debug'
        self.config: dict = config
        # basic configuration
        
        context.terminal = ['terminator', '-me']
        # debugger configuration

        self.execute: pwnlib.tubes.sock.sock = None
        # our process to interact
        self.server: Server = None
        # the server to be connected when using remote mode

        self.work_path = Path(argv[0]).parent
        self.elf_path = Path(config['elf']).resolve()
        self.elf = ELF(str(self.elf_path))

        self.inter_modified = bool(inter != None)
        self.needed_modified = bool(needed != None)

        if self.needed_modified:
            self.needed_path = [Path(lib).resolve() for lib in needed]
            self.lib = [ELF(str(lib_path)) for lib_path in self.needed_path]
        if self.inter_modified:
            self.inter_path = Path(inter).resolve()
            self.inter: pwnlib.elf.ELF = ELF(str(self.inter_path))
        
        self.parsed: lief.ELF.Binary = None
        # extend lief support


    def parse(self):
        self.parsed = lief.parse(str(self.elf_path))
        assert type(self.parsed) == lief.ELF.Binary
        return self.parsed


    def ensure_lib(self):
        if type(self.parsed) != lief.Binary:
            self.parse()
    
        exit_value = 0
        if self.inter_modified:
            command = f"patchelf --set-interpreter {str(self.inter_path)} {str(self.elf_path)}"
            log.info("Executing: " + command)
            exit_value = os.system(command)

        if self.needed_path == None:
            return -1
        
        lib_pattern = re.compile(r"lib[a-zA-Z]+")
        origin_path = [Path(lib) for lib in self.parsed.libraries]

        for origin, replace in itertools.product(origin_path, self.needed_path):
            if not re.findall(lib_pattern, origin.name)[0] in replace.name:
                continue
            command = f"patchelf --replace-needed {str(origin)} {str(replace)} {str(self.elf_path)}"
            log.info("Executing: " + command)
            exit_value += os.system(command)

        self.elf = ELF(str(self.elf_path))
        return exit_value
    
    # 启动进程
    def process_init(self):
        context.arch = self.elf.get_machine_arch()
        context.log_level = self.log_level
        if self.mode == 'run' or self.mode == 'gdb':
            if not self.elf_path.exists():
                log.error("ELF file does not exist.")
                exit(1)
            
            self.debug_mode = bool(self.mode == 'gdb')
            self.execute = process([str(self.elf_path)])

        elif self.mode == 'remote':
            self.server = Server(self.config['server'], self.config['server_class'])
            try:
                self.execute = self.server.connect()
            except exception.PwnlibException:
                log.error("Remote server error.")

        else:
            log.error("Parameter Error.")

        self.execute = add_features(self.execute)
        return self.execute
