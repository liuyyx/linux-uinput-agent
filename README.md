# linux-uinput-agent

在 Linux/X11 上**绕过应用层拦截**的鼠标键盘自动化。不走 XTEST（`xdotool` 那种会被 Firefox/Chromium 忽略的合成事件），而是直接往 `/dev/uinput` 写内核输入事件，系统把它当成一块真实的鼠标键盘设备。

## 为什么需要它

`xdotool` / `pyautogui` / `cua-driver` 走的是 XTest 或 XSendEvent。现代浏览器（Firefox、Chromium）和不少 Electron 应用会**忽略非真实设备发来的事件**，表现为「光标动了，但点不动」。

本项目创建一块虚拟 HID 设备挂在 X server 上，应用无法区分它和真鼠标。

## 依赖

```bash
sudo apt install python3-evdev
# 或
pip install evdev
```

需要 `/dev/uinput` 可写：

```bash
ls -l /dev/uinput
# crw-rw-rw- 1 root root 10, 223  → 普通人可写，OK
# crw-------  → 加 udev 规则：
echo 'KERNEL=="uinput", MODE="0666"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload && sudo udevadm trigger
```

## 用法

### 方式一：命令行单次（简单，但每次会新建销毁设备）

```bash
python3 uinput_ctl.py move 800 600
python3 uinput_ctl.py click
python3 uinput_ctl.py moveclick 244 344
```

⚠️ 设备新建后要等 X 注册（约 0.3s），频繁调用有延迟。

### 方式二：常驻 daemon（推荐）

```bash
# 终端 A
python3 vmouse_daemon.py

# 终端 B —— 通过命令文件驱动
echo "moveclick 244 344" > /tmp/hermes_mouse.cmd
echo "click" > /tmp/hermes_mouse.cmd
echo "type hello" > /tmp/hermes_mouse.cmd
echo "key enter" > /tmp/hermes_mouse.cmd
```

daemon 常驻后设备一直在，X 能稳定注册：

```bash
xinput list --short | grep hermes
# ↳ hermes-vmouse    id=15  [slave pointer  (2)]
# ↳ hermes-vkbd      id=16  [slave keyboard (3)]
```

## 命令表

| 命令 | 作用 |
|---|---|
| `move X Y` | 绝对定位（部分 X 不认 ABS，见下方坑） |
| `relmove DX DY` | 相对位移（最可靠） |
| `click` | 左键单击 |
| `rightclick` | 右键单击 |
| `dblclick` | 双击 |
| `moveclick X Y` | 移动后点击 |
| `type 文本` | 逐字符输入（仅 ASCII，中文需另想办法） |
| `key enter/esc/tab/space/backspace` | 单键 |

## 坑

1. **ABS 绝对定位在部分 X server 上无效**，光标不动。此时用 `xdotool mousemove X Y` 定位（它是精确的，只是点不动），再用本项目的 `click` 发送点击——这个组合最稳。
2. **REL 相对位移有 DPI 缩放误差**（实测 1920 屏上 314px 位移只走了 277px）。要么迭代逼近，要么用 xdotool 定位。
3. **设备必须常驻**。一次性脚本创建后立刻 `close()`，X 来不及注册，`xinput list` 里看不到设备。用 daemon。
4. **弹窗 / 模态层可能仍然点不动**。这不是事件层的问题——某些前端框架给遮罩层挂了 pointer-events 拦截，或者按钮在 iframe 里。这时候按键（Tab + Enter）或者放弃自动化更划算。
5. **中文输入**：evdev 的 keymap 只能打 ASCII。要打中文，用 `fcitx5` 的 DBus 接口，或者 Ctrl+Shift+U 走 Unicode 组合键。

## 实测环境

- Linux Mint 22.3 / XFCE / X11 / 1920×1080
- Python 3.12 + evdev
- 成功点击：Firefox 里的网页复选框、工具栏按钮
- 失败场景：网页模态弹窗内的按钮

## License

MIT
