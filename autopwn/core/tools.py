from pwnlib.util.packing import p64
from pwnlib.util.packing import pack

ARCH_x64 = 64
ARCH_x86 = 32

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

class Fastbins(Heap):
    def __init__(self, arch):
        super().__init__(self, arch)
        self.MAX_FAST_SIZE = 80 * self.SIZE_SZ / 4
        # 有效的fastbin每个块的最大大小
        self.DEFAULT_MXFAST = 64 * self.SIZE_SZ / 4
        # 默认的fastbin每个块的最大大小
        self.NFASTBINS = self.fastbin_index(self.request2size(self.MAX_FAST_SIZE) + 1)
        # fastbins中chunk的总数


    # sz为堆块的总大小
    def fastbin_index(self, sz):
        res = (sz >> (4 if self.SIZE_SZ == 8 else 3)) - 2
        return res

class Bins(Heap):
    def __init__(self, arch):
        super().__init__(arch)
        self.NBINS = 128
        self.NSMALLBINS = 64
        self.SMALLBIN_WIDTH = self.MALLOC_ALIGNMENT
        self.SMALLBIN_CORRECTION = (self.MALLOC_ALIGNMENT > 2 * self.SIZE_SZ)
        self.MIN_LARGE_SIZE = ((self.NSMALLBINS - self.SMALLBIN_CORRECTION) * self.SMALLBIN_WIDTH)
        
    def in_smallbin_range(self, sz) :
        return sz < self.MIN_LARGE_SIZE

    def smallbin_index(self, sz):
        res = (sz >> 4 if self.SMALLBIN_WIDTH == 16 else sz >> 3) + self.SMALLBIN_CORRECTION
        return res
    
    @staticmethod
    def largebin_index_32(sz):
        if mid := (sz >> 6) <= 38:
            return 56 + mid
        if mid := (sz >> 9) <= 20:
            return 91 + mid
        if mid := (sz >> 12) <= 10:
            return 110 + mid
        if mid := (sz >> 15) <= 4:
            return 119 + mid
        if mid := (sz >> 18) <= 2:
            return 124 + mid
        return 126

    @staticmethod
    def largebin_index_32_big(sz):
        if mid := (sz >> 6) <= 45:
            return 49 + mid
        if mid := (sz >> 9) <= 20:
            return 91 + mid
        if mid := (sz >> 12) <= 10:
            return 110 + mid
        if mid := (sz >> 15) <= 4:
            return 119 + mid
        if mid := (sz >> 18) <= 2:
            return 124 + mid
        return 126

    @staticmethod
    def largebin_index_64(sz):
        if mid := (sz >> 6) <= 48:
            return 48 + mid
        if mid := (sz >> 9) <= 20:
            return 91 + mid
        if mid := (sz >> 12) <= 10:
            return 110 + mid
        if mid := (sz >> 15) <= 4:
            return 119 + mid
        if mid := (sz >> 18) <= 2:
            return 124 + mid
        return 126

    def largebin_index(self, sz):
        if self.SIZE_SZ == 8:
            return self.largebin_index_64(sz)
        if self.MALLOC_ALIGNMENT == 16:
            return self.largebin_index_32_big(sz)
        return self.largebin_index_32(sz)

    def bin_index(self, sz):
        if self.in_smallbin_range(sz):
            return self.smallbin_index(sz)
        return self.largebin_index(sz)


class Unsortedbins(Heap):
    def __init__(self, arch):
        super().__init__(arch)
    
    def __getitem__(self, key):
        pass

class Heap:
    def __init__(self, arch):
        self.arch = arch
        
        self.SIZE_SZ = self.arch / 8
        # 表示平台字长
        self.MALLOC_ALIGNMENT = 2 * self.SIZE_SZ
        # malloc函数分配块的最小单位
        self.MALLOC_ALIGN_MASK = self.MALLOC_ALIGNMENT - 1
        # malloc块对齐掩码
        self.MIN_CHUNK_SIZE = 4 * self.SIZE_SZ
        # 最小的可能的块大小
        self.MINSIZE = (self.MIN_CHUNK_SIZE + self.MALLOC_ALIGN_MASK) & (~self.MALLOC_ALIGN_MASK)
        # 最小块大小

        self.fastbins = Fastbins(arch)
        self.chunk = Chunk(arch)
        self.bins = Bins(arch)


class Chunk(Heap):
    def __init__(self, arch):
        super().__init__(self, arch)
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

    def __bytes__(self):
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
            byte = bytes(self)
            start = self.SIZE_SZ * key.start
            stop = self.SIZE_SZ * key.stop
            return byte[start:stop]
        else:
            print("Not Supported.")
            return None
        
