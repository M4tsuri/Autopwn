from pwnlib import gdb
from autopwn.ctf.attack import Attack

class Debug:
    def __init__(self, dbg_obj: Attack):
        self.pie = dbg_obj.elf.pie
        self.ex = dbg_obj.execute
        self.dbg_on = dbg_obj.debug_mode
        self.elf_path = dbg_obj.elf_path
        self.script = '\n'
        self.real_addr = lambda addr: f"$rebase({hex(addr)})" if self.pie else hex(addr)
        
    def b(self, *points):
        baddr_str = "b *{}\n"
        bfunc_str = "b {}\n"
        for point in points:
            if type(point) == type('deadbeef'):
                self.script += bfunc_str.format(point)
            elif type(point) == type(0xdeadbeef):
                self.script += baddr_str.format(self.real_addr(point))
        return self

    def c(self):
        self.script += "continue\n"
        return self

    def watch(self, points, mode='rw'):
        if 'r' in mode and 'w' in mode:
            watch_str = "awatch *{}"
        elif 'r' in mode:
            watch_str = "rwatch *{}"
        elif 'w' in mode:
            watch_str = "watch *{}"

        for point in points:
            self.script += watch_str.format(self.real_addr(point))
        
        return self

    def catch(self, *args):
        catch_str = 'catch '
        for part in args:
            catch_str += str(part) + ' '
        self.script += catch_str
        return self

    def attach(self):
        if self.dbg_on:
            gdb.attach(self.ex, self.script)


    def cmd(self, command):
        self.script += (command + '\n')
        return self

    def start(self):
        return gdb.debug(self.elf_path, self.script)
