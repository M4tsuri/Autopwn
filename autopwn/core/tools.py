from pwnlib.util.packing import p64
from pwnlib.util.packing import pack
from pwnlib.log import Logger
from pwnlib import gdb
from autopwn.ctf.attack import Attack

log = Logger()


ARCH_x64 = 64
ARCH_x86 = 32
PREV_INUSE = 1
PREV_NOT_INUSE = 0
MMAPPED = 1
NOT_MMAPPED = 0
MAIN_ARENA = 0
NOT_MAIN_ARENA = 1
SMALLER = 0
LARGER = 1
SINGLE_LINKED = 0
DOUBLE_LINKED = 1

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

class Heap:
    def __init__(self, attack_obj: Attack):
        self.arch = attack_obj.elf.bits

        self.SIZE_SZ = self.arch // 8
        # 表示平台字长
        self.MALLOC_ALIGNMENT = 2 * self.SIZE_SZ
        # malloc函数分配块的最小单位
        self.MALLOC_ALIGN_MASK = self.MALLOC_ALIGNMENT - 1
        # malloc块对齐掩码
        self.MIN_CHUNK_SIZE = 4 * self.SIZE_SZ
        # 最小的可能的块大小
        self.MINSIZE = (self.MIN_CHUNK_SIZE + self.MALLOC_ALIGN_MASK) & (~self.MALLOC_ALIGN_MASK)
        # 最小块大小

        # Fastbins
        self.MAX_FAST_SIZE = 80 * self.SIZE_SZ // 4
        # 有效的fastbin每个块的最大大小
        self.DEFAULT_MXFAST = 64 * self.SIZE_SZ // 4
        # 默认的fastbin每个块的最大大小
        self.NFASTBINS = self.fastbin_index(self.request2size(self.MAX_FAST_SIZE) + 1)
        # fastbins中chunk的总数

        self.TCACHE_MAX_BINS = 64
        self.MAX_TCACHE_SIZE = self.tidx2usize(self.TCACHE_MAX_BINS - 1)

        # Bins
        self.NBINS = 128
        self.NSMALLBINS = 64
        self.SMALLBIN_WIDTH = self.MALLOC_ALIGNMENT
        self.SMALLBIN_CORRECTION = (self.MALLOC_ALIGNMENT > 2 * self.SIZE_SZ)
        self.MIN_LARGE_SIZE = ((self.NSMALLBINS - self.SMALLBIN_CORRECTION) * self.SMALLBIN_WIDTH)

    def request2size(self, req):
        out = req + self.SIZE_SZ + self.MALLOC_ALIGN_MASK
        if out < self.MINSIZE:
            return self.MINSIZE
        else:
            res = out & (~self.MALLOC_ALIGN_MASK)
            return res

    def aligned_OK(self, size):
        if size < self.MINSIZE:
            return False
        return bool((size & self.MALLOC_ALIGN_MASK) == 0)

    def size2request(self, size, tend=LARGER):
        if size == 0:
            return 0
        if not self.aligned_OK(size):
            log.error("Invalid chunk size.")
            return None
        form_size = size - self.SIZE_SZ * 2
        if tend == LARGER:
            req = form_size + self.SIZE_SZ
        elif tend == SMALLER:
            req = form_size - self.MALLOC_ALIGN_MASK + self.SIZE_SZ
        else:
            log.error("Invalid tend.")
            return None
        assert(size == self.request2size(req))
        return req

    # this is the real size we get in chunk 
    def userSize(self, req):
        padded = self.request2size(req)
        if req + 2 * self.SIZE_SZ > padded:
            return padded - self.SIZE_SZ
        return padded - 2 * self.SIZE_SZ
    
    def maxSize(self, req):
        padded = self.request2size(req)
        return padded - self.SIZE_SZ
    
    def formSize(self, req):
        padded = self.request2size(req)
        return padded - 2 * self.SIZE_SZ

    @staticmethod
    def setBit(num, idx, bit):
        mask = bit << idx
        num = num | mask
        return num

    # sz为堆块的总大小
    def fastbin_index(self, sz):
        return (sz >> (4 if self.SIZE_SZ == 8 else 3)) - 2
        
    def in_smallbin_range(self, sz) :
        return sz < self.MIN_LARGE_SIZE

    def smallbin_index(self, sz):
        res = (sz >> 4 if self.SMALLBIN_WIDTH == 16 else sz >> 3) + self.SMALLBIN_CORRECTION
        return res
    
    @staticmethod
    def largebin_index_32(sz):
        if (mid := (sz >> 6)) <= 38:
            return 56 + mid
        if (mid := (sz >> 9)) <= 20:
            return 91 + mid
        if (mid := (sz >> 12)) <= 10:
            return 110 + mid
        if (mid := (sz >> 15)) <= 4:
            return 119 + mid
        if (mid := (sz >> 18)) <= 2:
            return 124 + mid
        return 126

    @staticmethod
    def largebin_index_32_big(sz):
        if (mid := (sz >> 6)) <= 45:
            return 49 + mid
        if (mid := (sz >> 9)) <= 20:
            return 91 + mid
        if (mid := (sz >> 12)) <= 10:
            return 110 + mid
        if (mid := (sz >> 15)) <= 4:
            return 119 + mid
        if (mid := (sz >> 18)) <= 2:
            return 124 + mid
        return 126

    @staticmethod
    def largebin_index_64(sz):
        if (mid := (sz >> 6)) <= 48:
            return 48 + mid
        if (mid := (sz >> 9)) <= 20:
            return 91 + mid
        if (mid := (sz >> 12)) <= 10:
            return 110 + mid
        if (mid := (sz >> 15)) <= 4:
            return 119 + mid
        if (mid := (sz >> 18)) <= 2:
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

    def csize2tidx(self, sz):
        return (sz - self.MINSIZE + self.MALLOC_ALIGNMENT - 1) // self.MALLOC_ALIGNMENT

    def usize2tidx(self, x):
        return self.csize2tidx(self.request2size(x))

    def tidx2usize(self, idx):
        return idx * self.MALLOC_ALIGNMENT + self.MINSIZE - self.SIZE_SZ


class Chunk(Heap):
    def __init__(self, attack_obj: Attack):
        super().__init__(attack_obj)
        self.prev_size = 0
        self.size = -1
        self.norm_size = -1
        self.req_size = -1
        self.A = MAIN_ARENA
        self.M = NOT_MMAPPED
        self.P = PREV_INUSE
        self.fd = 0
        self.bk = 0
        self.fd_nextsize = 0
        self.bk_nextsize = 0
        self.cookie = 0
        self.link = SINGLE_LINKED

    def __bytes__(self):
        pword = lambda x : pack(x, self.SIZE_SZ * 8, 'little', False)
        payload = pword(self.prev_size)
        if self.size == -1:
            if self.norm_size == -1:
                self.norm_size = self.request2size(self.req_size)
            self.size = self.setBit(self.norm_size, 0, self.P)
            self.size = self.setBit(self.size, 1, self.M)
            self.size = self.setBit(self.size, 2, self.A)
            
        payload += pword(self.size)
        if self.link == SINGLE_LINKED:
            pword_c = lambda x : pword(x ^ self.cookie)
        else:
            pword_c = pword
        
        payload += pword_c(self.fd) + pword_c(self.bk)
        payload += pword(self.fd_nextsize) + pword(self.bk_nextsize)
        self.size = -1
        return payload

    def __getitem__(self, key):
        if isinstance(key, slice):
            byte = bytes(self)
            start = self.SIZE_SZ * (key.start if key.start else 0)
            stop = (self.SIZE_SZ * key.stop if key.stop else len(byte))
            return byte[start:stop]
        else:
            return self[key:key + 1]


class Debug:
    def __init__(self, dbg_obj: Attack):
        self.pie = dbg_obj.elf.pie
        self.ex = dbg_obj.execute
        self.dbg_on = dbg_obj.debug_mode
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
