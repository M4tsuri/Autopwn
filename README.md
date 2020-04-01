# Autopwn

Autopwn项目，致力于提供如下特性：

- 常见漏洞的exp模版
- 批量getshell，提交flag
- 对pwntools常用功能的更好的包装

```
.
├── \
├── autopwn
│   ├── awd
│   │   ├── attacker.py           # run exp to get shell on each target
│   │   ├── attack.py             # core module
│   │   ├── get_ip.py             # get target list
│   │   └── __init__.py
│   ├── core
│   │   ├── classes.py            # core classes like remote server
│   │   ├── __init__.py
│   │   └── pwn.py                # entrypoint of the whole framework
│   ├── ctf
│   │   ├── attack.py             # entrypoint for ctf framework
│   │   ├── __init__.py
│   │   ├── less_tube.py          # add more custom features for the tube class
│   │   └── stack.py              # visualization tool for stack
│   └── __init__.py
├── autopwn.conf                  # config file template
├── gen.py                        # script to generate config file
├── README.md
└── test
    ├── flag
    └── payload.py
```