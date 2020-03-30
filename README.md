# Autopwn

Autopwn项目，致力于提供如下特性：

- 常见漏洞的exp模版
- 批量getshell，提交flag
- 对pwntools常用功能的更好的包装

```
.
|-- __init__.py
|-- awd                AWD框架
|   |-- __init__.py
|   |-- attack.py      批量攻击主模块（用于统筹）
|   |-- attacker.py    攻击主模块（用于执行攻击）
|   `-- get_ip.py      获取靶机IP
|-- ctf                CTF框架
|   |-- __init__.py    
|   |-- less_tube.py   添加tube类方法
|   |-- pwning.py      主模块
|   `-- stack.py       可视化栈结构
`-- exp                序列化攻击流程
```