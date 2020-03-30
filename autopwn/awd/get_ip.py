import re
import pandas

ip_pattern = re.compile(r"\d+\.\d+\.\d+\.\d+")

def check_valid(ip):  # check if ip is valid and ask for a repairing
    if re.fullmatch(ip_pattern, ip):
        return ip
    else:
        while True:
            print "Invilad value found: " + ip
            print "Would you like to repair it? [Repaired/None]"
            repaired = input()
            if re.fullmatch(ip_pattern, repaired):
                return repaired
            else:
                ip = repaired

def add_form_txt(path):  # add target list from a txt file
    res = []
    with open(path, "r") as f:
        for line in f.readlines():
            res.append(line)

        res = pandas.Series(res, name="target")
        res = res.apply(check_valid)
        return res

        

    
            
