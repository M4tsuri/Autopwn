# coding=utf-8
import curses
from curses import textpad
import yaml
import io


class StackView:
    def __init__(self):
        self.stdscr = curses.initscr()  # 初始化屏幕
        self.maxyx = self.stdscr.getmaxyx()  # 屏幕最大长宽
        self.height = 50  # pad宽高
        self.width = self.maxyx[1] * 2
        self.pad_height = self.maxyx[0] - 2  # pad显示区域宽高
        self.pad_width = self.maxyx[1] - 1
        self.in_height = self.maxyx[0] - 1  # 输入区域宽高
        self.in_width = self.maxyx[1]
        self.pad = self.scrinit()
        self.inpad = self.inputinit()
        self.locxy = [0, 0]

    # 退出程序
    def scrclose(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        self.pad.keypad(False)
        curses.echo()
        curses.endwin()

    # 初始化
    def scrinit(self):
        pad = curses.newpad(self.height, self.width)  # 初始化显示区域
        curses.noecho()
        curses.cbreak()
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        pad.keypad(True)
        return pad

    # 输入框
    def inputinit(self):
        inpad = curses.newwin(2, self.in_width, self.in_height, 0)  # 初始化输入区域
        return inpad

    # 解析命令
    def parsecmd(self, cmd):
        if cmd == 'i':
            return 0
        elif cmd == 'p':
            self.locxy[0] -= self.pad_height - 3
            self.padrefresh()
        elif cmd == 'n':
            self.locxy[0] += self.pad_height - 3
            self.padrefresh()
        elif cmd == 'b':
            self.locxy[0] = self.height - self.maxyx[0] - 1
            self.locxy[1] = self.maxyx[1] / 2
            self.padrefresh()
        return 1

    # 进入命令行模式，获取命令
    def getcmd(self):
        curses.echo()
        curses.curs_set(1)
        while True:
            self.inpad.addstr(0, 0, '> ')
            res = self.parsecmd(self.inpad.getstr(0, 2))
            self.inpad.clear()
            self.inpad.refresh()
            if not res:
                break
        curses.noecho()
        curses.curs_set(0)

    def padrefresh(self):
        # 防止滚动超出边界
        if self.locxy[0] < 0:
            self.locxy[0] = 0
        elif self.locxy[0] >= self.height - self.maxyx[0]:
            self.locxy[0] = self.height - self.maxyx[0] - 1
        if self.locxy[1] < 0:
            self.locxy[1] = 0
        elif self.locxy[1] >= self.width:
            self.locxy[1] = self.width - 1
        self.pad.refresh(self.locxy[0], self.locxy[1], 0, 0, self.pad_height, self.pad_width)

    # 显示界面并提供基于方向键的滚动支持
    def scrscroll(self):
        self.locxy[0] = self.height - self.maxyx[0]
        self.locxy[1] = self.maxyx[1] / 2
        self.padrefresh()
        while True:
            inc = self.pad.getch()
            mouse = 0
            if inc == curses.KEY_MOUSE:
                mouse = int(curses.getmouse()[4])

            if inc == ord('q'):
                break
            if inc == curses.KEY_DOWN or mouse == 2097152:
                self.locxy[0] += 2
            elif inc == curses.KEY_UP or mouse == 65536:
                self.locxy[0] -= 2
            elif inc == curses.KEY_RIGHT:
                self.locxy[1] += 2
            elif inc == curses.KEY_LEFT:
                self.locxy[1] -= 2
            elif inc == ord(':'):
                self.getcmd()

            self.padrefresh()


# 带有文字内容和标注的文本框
class TextRect(object):
    def __init__(self, pad, upyx=None, size=0, text='', psize=0, mode=4):
        self.pad = pad
        self.maxyx = pad.getmaxyx()
        self.width = 16  # 文本框的宽度
        self.midx = (self.maxyx[1] - self.width) / 2  # pad中文本框的中间位置

        # 运行模式（32位或64位）
        self.X86 = 4
        self.X64 = 8
        self.mode = mode

        # 文本框的位置
        if upyx:
            self.upyx = upyx  # 文本框的左上角
        else:
            self.upyx = [self.maxyx[0] - 5, self.midx]
        self.height = int(self.sizetrans(size))  # 文本框的高

        # 文本框相关数据参数
        self.size = size  # 本文本框长度
        self.sum = size + psize  # 总长度
        self.text = text  # 文本框内容

    # 将栈中的偏移转化为文本框的高
    @staticmethod
    def sizetrans(src):
        maxsize = 4
        minsize = 2
        if 0 < src < 0x30:
            return minsize
        elif src <= 0:
            return 0
        else:
            return maxsize

    # 初始方框
    def initrect(self):
        # 加载方框
        loyx = [self.upyx[0] + self.height, self.upyx[1] + self.width]
        textpad.rectangle(self.pad, self.upyx[0], self.upyx[1], loyx[0], loyx[1])

        # 加载文本
        datayx = [0, 0]
        datayx[0] = self.upyx[0] + (self.height / 2)
        datayx[1] = self.upyx[1] + (self.width / 2 - len(self.text) / 2)
        self.pad.addstr(datayx[0], datayx[1], self.text)
        self.labelrect()

    # 连接多个方框
    def joinrect(self, size, text):
        newyx = [self.upyx[0] - self.sizetrans(size), self.upyx[1]]
        newrect = TextRect(self.pad, newyx, size, text, self.sum, self.mode)
        newrect.initrect()
        return newrect

    # 为方框加标注
    def labelrect(self):
        # 本方框的数据长度
        thisstr = '-' + hex(self.size)
        thisloc = [self.upyx[0], self.upyx[1] - 1 - len(thisstr)]
        self.pad.addstr(thisloc[0], thisloc[1], thisstr)

        # 总数据长度
        sumstr = '-' + hex(self.sum)
        sumloc = [self.upyx[0], self.upyx[1] + self.width + 2]
        self.pad.addstr(sumloc[0], sumloc[1], sumstr)

    def funcall(self):
        if self.mode == self.X86:
            return self.joinrect(self.X86, 'eip').joinrect(self.X86, 'ebp')
        elif self.mode == self.X64:
            return self.joinrect(self.X64, 'rip').joinrect(self.X64, 'rbp')
        else:
            raise ModeNotSetError


class ModeNotSetError(Exception):
    pass


class StackFile:
    def __init__(self, path):
        with io.open(path, mode='r', encoding='utf-8') as stackf:
            self.info = yaml.load(stackf, Loader=yaml.BaseLoader)
        self.parsed_funcs = self.parsefuncs(self.info['func'])
        self.scr = StackView()
        self.rect = TextRect(self.scr.pad)
        self.rect.mode = int(self.info['mode'])
        self.rect.initrect()

    @staticmethod
    def parsefuncs(funcs):
        # the first stage parse
        def parsefunc(this_func):
            info = {'name': this_func.keys()[0]}
            entity = this_func[info['name']]
            info['data_sum'] = int(entity['sum'], base=16)
            info['data'] = []
            init_template = {
                'name': 'padding',
                'size': 0x0,
                'addr': 0x0
            }  # basic unit template
            for data in entity['data']:
                init_template['name'] = data.keys()[0]
                init_template['addr'] = int(data[init_template['name']][0], base=16)
                init_template['size'] = int(data[init_template['name']][1], base=16)
                info['data'].append(init_template.copy())
                # when appending a dict to a list, python will only append a reference of the dict
            return info

        # the second stage parse
        def offset_calculate():
            data = func_info['data']
            data_num = len(func_info['data'])
            data_sum = func_info['data_sum']
            res = []
            data_template = {
                'name': 'padding',
                'size': 0x0
            }  # basic unit template

            # append data to res depending on size
            def append_data(data_size, data_name):
                if data_size > 0:
                    data_template['size'] = data_size
                    data_template['name'] = data_name
                    res.append(data_template.copy())
                else:
                    pass

            if data_num == 0:
                data_template['size'] = data_sum
                res.append(data_template.copy())
                return res
            elif data_num == 1:
                append_data(data[0]['addr'] - data[0]['size'], 'padding')
                append_data(data[0]['size'], data[0]['name'])
                append_data(data_sum - data[0]['addr'], 'padding')
            else:
                append_data(data[0]['addr'] - data[0]['size'], 'padding')
                for i in range(0, data_num):
                    # print str(data[i]['size']) + data[i]['name']
                    append_data(data[i]['size'], data[i]['name'])
                append_data(data_sum - data[data_num - 1]['addr'], 'padding')

            return res

        parse_res = []
        for func in funcs:
            func_info = parsefunc(func)
            # print func_info['name']
            func_template = {'name': func_info['name'], 'data': offset_calculate()}
            parse_res.append(func_template.copy())

        return parse_res

    def stackshow(self):
        tmp = self.rect
        for func in self.parsed_funcs:
            tmp = tmp.funcall()
            for data in func['data']:
                tmp = tmp.joinrect(data['size'], data['name'])

        self.scr.scrscroll()

    def close(self):
        self.scr.scrclose()
