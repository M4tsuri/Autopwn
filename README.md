# Autopwn

当前处于活跃开发的分支为全面迁移到python 3.8的dev分支，而即将被抛弃的master分支仅支持python2。
由于兼容性的问题，本分支不再提供对连接ida的支持。

## 简介

Autopwn项目，致力于提供如下特性：

- 简化exp
- 对pwntools常用功能的更好的包装

目前已经实现的功能：
- 对自定义函数的包装（不完善）
- 使用命令行参数启动脚本，从而实现不同的功能（local run，local debug，remote run）
- 允许用户自定义debug时的gdb脚本，添加了对PIE程序仅使用偏移下断点的支持
- 允许用户自行提供函数封装，并将其添加为tubes的方法，已内置数个别名
- 允许用户更改elf文件的库查找路径与解释器路径（使用patchelf以及lief实现）
- 允许用户为当前的elf生成一个可修改的lief Binary对象
- 添加Ubuntu常用库的数据库（ld，libc，libdl）

## 效果图

- 生成配置文件
![](https://github.com/CTSinon/Autopwn/blob/master/screenshots/autoconf.gif)

- 搭配emacs的YASnippet插件生成exp框架
![](https://github.com/CTSinon/Autopwn/blob/master/screenshots/genexp.gif)

- patchelf
![](https://github.com/CTSinon/Autopwn/blob/master/screenshots/autopatch.gif)

- 自带常用tube方法别名（如rl，sl，ru）
![](https://github.com/CTSinon/Autopwn/blob/master/screenshots/run.gif)

- 远程连接
![](https://github.com/CTSinon/Autopwn/blob/master/screenshots/remote.gif)

## 安装

### 依赖
- python 3.8.3 (environment)
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

//TODO

### 目录结构

```
.
├── \
├── autopwn
│   ├── awd                       # awd框架，未实现
│   │   ├── attacker.py           # //TODO
│   │   ├── attack.py             # //TODO
│   │   ├── get_ip.py             # 获取目标列表
│   │   └── __init__.py
│   ├── core
│   │   ├── classes.py            # 存放核心类
│   │   ├── __init__.py
│   │   ├── tools.py              # 存放常用的工具函数与工具类
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
- 感谢cnitlrt师傅的支持
- 作者没有专业研究过python这门语言，所以脚本写得一言难尽。设计模式之类的更是没怎么研究过。希望各路大神能提出更好的建议，添加更方便的功能，大家一起进步呀 (๑•̀ㅂ•́)و✧ 
