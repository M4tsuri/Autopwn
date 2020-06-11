from pwn import *
import autopwn
import re
import pwnlib

# config = {
#   'server_class': nc or ssh,
#   'flag_pattern': regex which  flag matches,
#   'flag': {
#       'ip': flag server ip,
#       'port': port,
#       'proto': proto,
#       'team': team
#   },
# }

class Attacker:
    def __init__(self, config):
        self.flag_addr = config['flag']['addr']
        self.token = config['flag']['tokens']
        self.team = config['flag']['team']
        self.server_class = config['server_class']

    def run(self, argv, qes):
        if argv[1] == 'self':
            self.targets
        self.targets.apply(self.attacker, axis=1)

    def attacker(self, target):
        if (execute = connector(self.server_class), target) == NULL:  # check connection to server
            return None
        exp(execute)
        flag = get_flag(execute)  # get flag
        if re.match(config['flag_pattern']):  # check if flag is valid
            pwnlib.flag.submit_flag(
                flag, 
                server=self.flag_ip, 
                port=self.flag_port, 
                proto=self.flag_proto,
                team=self.team
            )
            return flag
        return None

    @staticmethod    
    def connector(server_class, target):
        server = autopwn.core.classes.Server(target, server_class)
        try:
            execute = server.connect()
        except exception.PwnlibException as e:
            print("Remote server " + str(target) + "error.")  # error log
            return None
        return execute
