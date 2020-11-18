# the classes that may help when solving TLS related problems.
from ctypes import c_int64, Structure
def mask1(n):
    
    if n >= 0:
        return 2**n - 1
    else:
        return 0
    
def ror(n, d, width=8):
    d %= width * 8  #  width bytes give 8*bytes bits
    if d < 1:
        return n
    mask = mask1(8 * width)
    return ((n >> d) | (n << (8 * width - d))) & mask

def rol(n, d, width=8):
    d %= width * 8
    if d < 1:
        return n
    mask = mask1(8 * width)
    return ((n << d) | (n >> (width * 8 - d))) & mask

def ptr_demangle(ptr, key, LP_SIZE):
    tmp = ror(ptr, LP_SIZE * 2 + 1, LP_SIZE)
    return tmp ^ key
    
def ptr_mangle(ptr, key, LP_SIZE):
    tmp = ptr ^ key
    return rol(tmp, LP_SIZE * 2 + 1, LP_SIZE)

class dtor_list(Structure):
    _fields_ = [("func", c_int64),
                ("obj", c_int64),
                ("map", c_int64),
                ("next", c_int64)]

    def pack(self):
        return bytes(memoryview(self))