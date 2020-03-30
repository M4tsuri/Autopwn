import re
import os
import yaml

def parse_config():
    try:
        config_file = open("autopwn.conf")
        config = yaml.load(config_file)
        return config
    except FileNotFountError:
        print "Fatal: Configure File Not Found"
        exit(1)

def go(argv, exp, get_flag):
    config = parse_config()
    if config['class'] == 'ctf':
        from autopwn.ctf import attack
        a = attack.Attack(argv=argv, config=config)
        a.exp = exp
        a.get_flag = get_flag
        a.exp()
        flag = a.get_flag()
        print flag

    elif config['class'] == 'awd':
        from autopwn.awd import attack
        a = attack.Attack()
        a.exp = exp
        a.get_flag = get_flag
        a.run()

    else:
        print "Fatal: Wrong Competation Class."