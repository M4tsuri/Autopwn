import sys
from autopwn.pwning import *

sys.path.append("/mac/Users/ctsinon/Kali/pypwn")
conf_file = 'autopwn.conf'
pwnExec = Pwning(sys.argv, conf_file)
r = pwnExec.execute


r.interactive()
r.close()
