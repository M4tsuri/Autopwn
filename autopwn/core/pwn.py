import re
import os
import yaml
import pwnlib.tubes.tube

def parse_config():
    try:
        with open("autopwn.conf") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            return config
    except IOError:
        print "Fatal: Configure File Not Found"
        exit(1)

def go(argv, exp, get_flag):
    config = parse_config()
    if config['mode'] == 'ctf':
        from autopwn.ctf import attack
        ao = attack.Attack(argv=argv, config=config)
        a = ao.process_init()
        setattr(attack.Attack, 'exp', exp)
        setattr(attack.Attack, 'get_flag', get_flag)
        ao.exp(a)
        flag = ao.get_flag(a)
        print flag

    elif config['mode'] == 'awd':
        from autopwn.awd import attack
        a = attack.Attack()
        setattr(attack.Attack, 'exp', exp)
        setattr(attack.Attack, 'get_flag', get_flag)
        a.run()

    else:
        print "Fatal: Wrong Competation Class."