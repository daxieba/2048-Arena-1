"""一键打包：生成图标 -> PyInstaller 单文件 exe。"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    print(">", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def main():
    icon = os.path.join(ROOT, "tools", "app.ico")
    if not os.path.exists(icon):
        run([sys.executable, os.path.join(ROOT, "tools", "make_icon.py")])

    run([
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile", "--windowed",
        "--name", "2048-Arena-1",
        "--icon", icon,
        "--add-data", "game/assets" + os.pathsep + "game/assets",
        "--hidden-import", "webview.platforms.edgechromium",
        os.path.join(ROOT, "game", "app.py"),
    ])

    exe = os.path.join(ROOT, "dist", "2048-Arena-1.exe")
    print("\n完成：", exe)


if __name__ == "__main__":
    main()
