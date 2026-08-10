"""验证打包后的 exe：启动后应保持运行、页面正常初始化并通过桥接写入状态文件。

用法：python tools/verify_exe.py
"""
import ctypes
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "dist", "2048-Arena-1.exe")
STATE_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "ZCode2048")
STATE_FILE = os.path.join(STATE_DIR, "state.json")

assert os.path.exists(EXE), "未找到 " + EXE

if os.path.exists(STATE_DIR):
    shutil.rmtree(STATE_DIR)

print("启动 exe ...")
proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))


def window_titles():
    """枚举所有可见顶层窗口标题（去重）。"""
    titles = []
    seen = set()
    hwnds = []

    def cb(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(cb), 0)
    for h in hwnds:
        n = ctypes.windll.user32.GetWindowTextLengthW(h)
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            ctypes.windll.user32.GetWindowTextW(h, buf, n + 1)
            if buf.value and buf.value not in seen:
                seen.add(buf.value)
                titles.append(buf.value)
    return titles


ok = False
elapsed = 0
for step in (10, 15, 15):  # 最多等 40 秒（onefile 解压 + WebView2 首次初始化）
    time.sleep(step)
    elapsed += step
    if proc.poll() is not None:
        print("  ✗ exe 提前退出，退出码：", proc.returncode)
        sys.exit(1)
    if os.path.exists(STATE_FILE):
        ok = True
        break
    print("  已等 %d 秒，尚未生成状态文件" % elapsed)

if not ok:
    print("  ✗ 等待结束仍未生成状态文件")
    print("  当前窗口列表：", window_titles())

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = f.read()
    print("  ✓ 桥接状态文件已生成：")
    print("    " + data.replace("\n", "\n    "))
    ok = ("size" in data) and ("sound" in data) and ("best" in data)
    print("  ✓ 持久化字段完整" if ok else "  ✗ 持久化字段不完整")
    titles = window_titles()
    print("  窗口列表：", titles)

try:
    proc.terminate()
except OSError:
    pass
time.sleep(1)
if proc.poll() is None:
    proc.kill()
# onefile 会派生子进程，按镜像名彻底清理，避免残留占用 exe 文件
subprocess.run(["taskkill", "/F", "/IM", "2048-Arena-1.exe"], capture_output=True)
print("已关闭 exe")
