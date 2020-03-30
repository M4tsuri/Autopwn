import autopwn.ctf.pwning
import re
import pwnlib

# this module aims to add new methods to tube class.

def add_features(src):
    src.extnum = setattr(pwnlib.tubes.tube.tube, 'extnum', extnum)
    return src

# extract numbers with a given base from an output line
def extnum(self, base = 10):  
    res = []
    if base == 10:
        pattern = re.compile(r'\d+')
    elif base == 16:
        pattern = re.compile(r"[0-9a-fA-F]{4,}")
    else:
        return None

    src = self.recvline()
    res = re.findall(pattern, src)
    for i in range(0, len(res)):
        res[i] = int(res[i], base=base)
    return res


