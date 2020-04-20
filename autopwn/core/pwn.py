import re
import os
import yaml
import pwnlib.tubes.tube
from pwn import *

def parse_config():
    try:
        with open("autopwn.conf") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            return config
    except IOError:
        log.error("Fatal: Configure File Not Found")
        exit(1)

def go(argv, exp=None, get_flag=None, submit=None, targets=None, qes=None):
    config = parse_config()
    
    if config['mode'] == 'ctf':
        from autopwn.ctf import attack
        assert exp != None and get_flag != None
        setattr(attack.Attack, 'exp', exp)
        setattr(attack.Attack, 'get_flag', get_flag)
        ao = attack.Attack(argv=argv, config=config)
        a = ao.process_init()
        
        ao.exp(a)
        flag = ao.get_flag(a)
        a.success(flag)

    elif config['mode'] == 'awd':
        assert (submit != None and targets != None and qes != None)
        from autopwn.awd import attacker
        a = attacker.Attacker(config)
        setattr(attacker.Attacker, 'targets', targets)
        setattr(attacker.Attacker, 'submit', submit)
        setattr(attacker.Attacker, 'exp', exp)
        setattr(attacker.Attacker, 'get_flag', get_flag)
        a.run(argv=argv, qes=qes)

    else:
        log.error("Fatal: Wrong Competition Class.")
