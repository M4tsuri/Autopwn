import re
import os
import yaml
from pwnlib.log import Logger
from time import sleep
from pwn import context

log = Logger()


def parse_config():
    try:
        with open("autopwn.conf") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            return config
    except EnvironmentError:
        log.error("Fatal: Configure File Not Found")
        exit(1)


def awd(argv, inter=None, needed=None, gap=10 * 60):
    config = parse_config()
    # parse configuration file
    
    from autopwn.ctf.attack import Attack

    if needed and (type(needed) != list):
        needed = [needed]


    attack_obj = Attack(argv=[argv[0], 'remote'], config=config, inter=inter, needed=needed)

    assert(hasattr(attack_obj, 'ip_list'))
    assert(hasattr(attack_obj, 'get_flag'))
    assert(hasattr(attack_obj, 'submit_flag'))
    assert(hasattr(attack_obj, 'exp'))
    assert(hasattr(attack_obj, 'replay'))

    ip_list = attack_obj.ip_list()
    host_count = len(ip_list)
    log.info(f"Totally {host_count} hosts.")
    turn_count = 0
    attack_obj.log_level = 'info'

    while True:
        success_count = 0
        for ip in attack_obj.ip_list():
            try:
                log.info("Attacking " + ip)
                attack_obj.config['server']['ip_port'] = ip
                tube = attack_obj.replay()
                attack_obj.exp(tube)
                flag = attack_obj.get_flag(tube).decode()
                res = attack_obj.submit_flag(flag)
                if res:
                    log.success("Success, flag is " + flag)
                    success_count += 1
                else:
                    log.success("Wrong flag: " + flag)
                print("")
            except BaseException as e:
                log.warning(f"Error: {e}")
        
        turn_count += 1
        log.info(f"Turn {turn_count}, {success_count} succeeded, {host_count - success_count} failed.")
        print("")
        sleep(gap)
    return attack_obj


def ctf(argv, inter=None, needed=None, gap=60 * 10):
    if argv[1] == 'awd':
        return awd(argv, inter, needed, gap)

    config = parse_config()
    # parse configuration file
    
    from autopwn.ctf.attack import Attack
    if needed and (type(needed) != list):
        needed = [needed]

    attack_obj = Attack(argv=argv, config=config, inter=inter, needed=needed)

    assert(hasattr(attack_obj, 'get_flag'))
    assert(hasattr(attack_obj, 'exp'))
    
    if argv[1] == 'patch' and (inter or needed):
        if not attack_obj.ensure_lib():
            log.success("ELF File Modified.")
        else:
            log.failure("ELF File Modifying Failed.")
        exit(0)
    
    tube = attack_obj.process_init()
    
    ret_val = attack_obj.exp(tube)

    if ret_val == None:
        flag = attack_obj.get_flag(tube)
        tube.success(flag)
        return attack_obj
    
    assert(hasattr(attack_obj, 'replay'))
    
    while ret_val != True:
        tube = attack_obj.replay()
        if tube == False:
            break
        ret_val = attack_obj.exp(tube)

    flag = attack_obj.get_flag(tube)
    log.success(flag)
    return attack_obj
