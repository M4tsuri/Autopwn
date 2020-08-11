from autopwn.ctf.attack import Attack

SUBMIT_FLAG = 'submit_flag'
GET_FLAG = 'get_flag'
EXP = 'exp'
REPLAY = 'replay'

operations = (SUBMIT_FLAG, GET_FLAG, EXP, REPLAY)

def attacker(name):
    def register_func(func):
        assert(name in operations)
        setattr(Attack, name, func)
        return func
    return register_func
