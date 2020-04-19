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

目前已经实现的功能：
- 对自定义函数的包装（不完善）
- 使用命令行参数启动脚本，从而实现不同的功能（local run，local debug，remote run）

TODO：
- 允许用户自定义debug时的gdb脚本，尤其要添加对PIE程序仅使用偏移下断点的支持
- 允许用户自行提供函数封装，并将其添加为tubes的方法（允许用户为常用函数设置别名）
- 允许用户更改elf文件的库查找路径与解释器路径（使用lief实现）
- 将项目与LibcSearcher集成
- 添加对lief库的支持，允许用户便捷的获取一个可编辑的elf对象
- 添加Ubuntu常用库的数据库（ld，libc，libdl）
