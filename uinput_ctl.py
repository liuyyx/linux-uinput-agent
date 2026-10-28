#!/usr/bin/env python3
"""内核级虚拟鼠标/键盘：直接通过 /dev/uinput 发事件，应用无法拦截。
用法:
  uinput_ctl.py move X Y
  uinput_ctl.py click [left|right]
  uinput_ctl.py type "文本"
  uinput_ctl.py key enter
"""
import sys, time, os
from evdev import UInput, ecodes as e, AbsInfo

SCREEN_W, SCREEN_H = 1920, 1080

CAP = {
    e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(0, 0, SCREEN_W, 0, 0, 0)),
        (e.EV_ABS, AbsInfo(0, 0, 0, 0, 0, 0)),
        (e.ABS_Y, AbsInfo(0, 0, SCREEN_H, 0, 0, 0)),
    ],
}
# 修掉上面写错的占位
CAP[e.EV_ABS] = [
    (e.ABS_X, AbsInfo(0, 0, SCREEN_W, 0, 0, 0)),
    (e.ABS_Y, AbsInfo(0, 0, SCREEN_H, 0, 0, 0)),
]


def make_mouse():
    return UInput(CAP, name="hermes-vmouse", version=0x1)


def move(ui, x, y):
    ui.write(e.EV_ABS, e.ABS_X, int(x))
    ui.write(e.EV_ABS, e.ABS_Y, int(y))
    ui.syn()


def click(ui, button=e.BTN_LEFT):
    ui.write(e.EV_KEY, button, 1)
    ui.syn()
    time.sleep(0.04)
    ui.write(e.EV_KEY, button, 0)
    ui.syn()


def make_keyboard():
    return UInput({
        e.EV_KEY: [e.KEY_LEFTSHIFT, e.KEY_LEFTCTRL, e.KEY_LEFTALT,
                   e.KEY_A, e.KEY_C, e.KEY_V, e.KEY_ENTER, e.KEY_ESC,
                   e.KEY_TAB, e.KEY_SPACE, e.KEY_BACKSPACE,
                   e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4, e.KEY_5,
                   e.KEY_6, e.KEY_7, e.KEY_8, e.KEY_9, e.KEY_0],
    }, name="hermes-vkbd", version=0x1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "move":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        ui = make_mouse()
        time.sleep(0.3)
        move(ui, x, y)
        time.sleep(0.2)
        ui.close()
        print(f"moved to {x},{y}")
    elif cmd == "click":
        btn = e.BTN_RIGHT if len(sys.argv) > 2 and sys.argv[2] == "right" else e.BTN_LEFT
        ui = make_mouse()
        time.sleep(0.3)
        click(ui, btn)
        time.sleep(0.2)
        ui.close()
        print("clicked")
    elif cmd == "moveclick":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        ui = make_mouse()
        time.sleep(0.3)
        move(ui, x, y)
        time.sleep(0.35)
        click(ui)
        time.sleep(0.2)
        ui.close()
        print(f"moved+clicked {x},{y}")
    else:
        print(__doc__)
