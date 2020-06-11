import re
import os
import yaml
from pwnlib.log import Logger

log = Logger()

def parse_config():
    try:
        with open("autopwn.conf") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            return config
    except EnvironmentError:
        log.error("Fatal: Configure File Not Found")
        exit(1)

def awd(argv, exp=None, get_flag=None, submit=None, targets=None, qes=None):
    config = parse_config()

    assert (exp != None and get_flag != None and submit != None and targets != None and qes != None)
    from autopwn.awd import attacker
    a = attacker.Attacker(config)
    setattr(attacker.Attacker, 'targets', targets)
    setattr(attacker.Attacker, 'submit', submit)
    setattr(attacker.Attacker, 'exp', exp)
    setattr(attacker.Attacker, 'get_flag', get_flag)
    a.run(argv=argv, qes=qes)


def ctf(argv, exp=None, get_flag=None, bp=None, inter=None, needed=None):
    config = parse_config()
    # parse configuration file

    if exp == None or get_flag == None:
        log.error("Exp or Get_flag function not provided.")
        exit(1)
    
    from autopwn.ctf import attack
    setattr(attack.Attack, 'exp', exp)
    setattr(attack.Attack, 'get_flag', get_flag)
    ao = attack.Attack(argv=argv, config=config, inter=inter, needed=needed)
    
    if bp:
        ao.breakat(bp)
    if argv[1] == 'patch' and (inter or needed):
        if not ao.ensurelib():
            log.success("ELF File Modified.")
        else:
            log.failure("ELF File Modifying Failed.")
        exit(0)
    
    a = ao.process_init()
    
    ao.exp(a)
    flag = ao.get_flag(a)
    a.success(flag)
