#!/usr/bin/env python3
"""常驻虚拟鼠标 daemon：设备一直存在，X 才能注册。
命令通过 /tmp/hermes_mouse.cmd 传递，格式：
  move X Y
  click
  rightclick
  dblclick
  type <文本>
"""
import os, time, sys, threading
from evdev import UInput, ecodes as e, AbsInfo

CMD = "/tmp/hermes_mouse.cmd"
W, H = 1920, 1080

CAP = {
    e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(0, 0, W, 0, 0, 0)),
        (e.ABS_Y, AbsInfo(0, 0, H, 0, 0, 0)),
    ],
    e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL],
}

ui = UInput(CAP, name="hermes-vmouse", version=0x1)
print("vmouse ready", flush=True)

# 同时建一个键盘
KB = UInput({
    e.EV_KEY: [e.KEY_A, e.KEY_B, e.KEY_C, e.KEY_D, e.KEY_E, e.KEY_F, e.KEY_G,
               e.KEY_H, e.KEY_I, e.KEY_J, e.KEY_K, e.KEY_L, e.KEY_M, e.KEY_N,
               e.KEY_O, e.KEY_P, e.KEY_Q, e.KEY_R, e.KEY_S, e.KEY_T, e.KEY_U,
               e.KEY_V, e.KEY_W, e.KEY_X, e.KEY_Y, e.KEY_Z,
               e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4, e.KEY_5, e.KEY_6, e.KEY_7,
               e.KEY_8, e.KEY_9, e.KEY_0, e.KEY_SPACE, e.KEY_ENTER, e.KEY_ESC,
               e.KEY_TAB, e.KEY_BACKSPACE, e.KEY_DOT, e.KEY_SLASH, e.KEY_MINUS,
               e.KEY_LEFTSHIFT, e.KEY_LEFTCTRL],
}, name="hermes-vkbd", version=0x1)
print("vkbd ready", flush=True)

KEYMAP = {
    'a': e.KEY_A, 'b': e.KEY_B, 'c': e.KEY_C, 'd': e.KEY_D, 'e': e.KEY_E,
    'f': e.KEY_F, 'g': e.KEY_G, 'h': e.KEY_H, 'i': e.KEY_I, 'j': e.KEY_J,
    'k': e.KEY_K, 'l': e.KEY_L, 'm': e.KEY_M, 'n': e.KEY_N, 'o': e.KEY_O,
    'p': e.KEY_P, 'q': e.KEY_Q, 'r': e.KEY_R, 's': e.KEY_S, 't': e.KEY_T,
    'u': e.KEY_U, 'v': e.KEY_V, 'w': e.KEY_W, 'x': e.KEY_X, 'y': e.KEY_Y,
    'z': e.KEY_Z, '0': e.KEY_0, '1': e.KEY_1, '2': e.KEY_2, '3': e.KEY_3,
    '4': e.KEY_4, '5': e.KEY_5, '6': e.KEY_6, '7': e.KEY_7, '8': e.KEY_8,
    '9': e.KEY_9, ' ': e.KEY_SPACE, '.': e.KEY_DOT, '/': e.KEY_SLASH,
    '-': e.KEY_MINUS,
}


def do_move(x, y):
    # 绝对定位（部分 X 不认，保留兼容）
    ui.write(e.EV_ABS, e.ABS_X, int(x))
    ui.write(e.EV_ABS, e.ABS_Y, int(y))
    ui.syn()


def do_relmove(dx, dy):
    ui.write(e.EV_REL, e.REL_X, int(dx))
    ui.write(e.EV_REL, e.REL_Y, int(dy))
    ui.syn()


def do_click(btn=e.BTN_LEFT, n=1):
    for _ in range(n):
        ui.write(e.EV_KEY, btn, 1)
        ui.syn()
        time.sleep(0.06)
        ui.write(e.EV_KEY, btn, 0)
        ui.syn()
        time.sleep(0.08)


def do_type(text):
    for ch in text:
        code = KEYMAP.get(ch.lower())
        if code is None:
            continue
        KB.write(e.EV_KEY, code, 1)
        KB.syn()
        time.sleep(0.02)
        KB.write(e.EV_KEY, code, 0)
        KB.syn()
        time.sleep(0.03)


def do_key(name):
    m = {'enter': e.KEY_ENTER, 'esc': e.KEY_ESC, 'tab': e.KEY_TAB,
         'space': e.KEY_SPACE, 'backspace': e.KEY_BACKSPACE}
    code = m.get(name)
    if code:
        KB.write(e.EV_KEY, code, 1)
        KB.syn()
        time.sleep(0.03)
        KB.write(e.EV_KEY, code, 0)
        KB.syn()


while True:
    try:
        if os.path.exists(CMD):
            with open(CMD) as f:
                raw = f.read().strip()
            os.remove(CMD)
            if raw:
                parts = raw.split(" ", 2)
                op = parts[0]
                if op == "move" and len(parts) >= 3:
                    do_move(parts[1], parts[2])
                elif op == "click":
                    do_click()
                elif op == "rightclick":
                    do_click(e.BTN_RIGHT)
                elif op == "dblclick":
                    do_click(n=2)
                elif op == "type" and len(parts) >= 2:
                    do_type(parts[1] if len(parts) == 2 else parts[1] + " " + parts[2])
                elif op == "key" and len(parts) >= 2:
                    do_key(parts[1])
                elif op == "relmove" and len(parts) >= 3:
                    do_relmove(parts[1], parts[2])
                elif op == "moveclick" and len(parts) >= 3:
                    do_move(parts[1], parts[2])
                    time.sleep(0.25)
                    do_click()
        time.sleep(0.03)
    except KeyboardInterrupt:
        break
    except Exception as ex:
        print("err:", ex, flush=True)
        time.sleep(0.2)
