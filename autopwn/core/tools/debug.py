from pwnlib import gdb

class Debug:
    def __init__(self, dbg_obj):
        self.proc = dbg_obj
        self.pie = dbg_obj.elf.pie
        self.ex = dbg_obj.execute
        self.params = dbg_obj.argv[2:]
        self.dbg_on = dbg_obj.debug_mode
        self.elf_path = dbg_obj.elf_path
        self.attached = dbg_obj.gdb_attached
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
        modes = {
            'w': "awatch *{}",
            'r': "rwatch *{}",
            'rw': "watch *{}"
        }
        
        watch_str = modes[mode]

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
        if self.dbg_on and not self.proc.gdb_attached:
            self.proc.gdb_attached = True
            gdb.attach(self.ex, self.script)


    def cmd(self, command):
        self.script += (command + '\n')
        return self

    def start(self):
        if self.proc.gdb_attached:
            return None
        self.proc.gdb_attached = True
        return gdb.debug([str(self.elf_path)] + self.params, self.script)
