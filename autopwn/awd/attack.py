from autopwn.awd import attacker
import autopwn.core.classes

class Attack:
    def __init__(self, config):
        self.exp = 0
        self.get_flag = 0
        self.config = config
        self.attacker = 0

    def attack(self):
        assert self.exp != 0 and self.get_flag != 0 and self.attacker != 0
        targets = get_ip.add_from_txt(config['targets'])
        targets.apply(attacker.attacker)

    def new_attack(self, exp, get_flag):
        self.exp = exp
        self.get_flag = get_flag
        self.attacker = attacker.Attacker(self.config, self.exp, self.get_flag)

