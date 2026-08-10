"""2048 桌面应用入口。

使用 pywebview（WebView2 / EdgeChromium）承载内嵌 HTML5 游戏，
并通过 js_api 提供本地状态持久化。
"""
import json
import os
import sys

import webview

APP_NAME = "ZCode2048"
STATE_FILE = os.path.join(
    os.environ.get("APPDATA") or os.path.expanduser("~"), APP_NAME, "state.json"
)


class Api:
    """暴露给前端 JS 的桥接 API（window.pywebview.api）。"""

    def load_state(self):
        """读取持久化的偏好设置（最高分 / 主题 / 音效 / 棋盘尺寸）。"""
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def save_state(self, data):
        """保存偏好设置。"""
        print("[bridge] save_state called:", data, flush=True)
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False


def resource_path(name):
    """定位打包后（PyInstaller _MEIPASS）或源码运行时的资源文件。"""
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, "game", "assets", name)
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game", "assets", name
    )


def main():
    api = Api()
    try:
        window = webview.create_window(
            "2048 Arena-1",
            resource_path("index.html"),
            js_api=api,
            width=540,
            height=800,
            min_size=(480, 700),
            resizable=True,
            background_color="#faf8ef",
        )

        def _diagnose():
            """诊断模式（ZCODE2048_DIAGNOSE=1 时启用）：把页面内部状态写入 state.json 便于排障。"""
            if not os.environ.get("ZCODE2048_DIAGNOSE"):
                return
            import time

            time.sleep(5)
            try:
                info = {
                    "diag": window.evaluate_js(
                        "JSON.stringify({"
                        "errs: window.__errs || [], "
                        "bridge: !!(window.pywebview && window.pywebview.api), "
                        "tiles: document.querySelectorAll('.tile').length, "
                        "sel: (document.getElementById('selSize')||{}).value, "
                        "title: document.title, "
                        "url: location.href})"
                    )
                }
                os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(info, f, ensure_ascii=False, indent=2)
            except Exception as exc:  # noqa: BLE001
                try:
                    with open(STATE_FILE, "w", encoding="utf-8") as f:
                        json.dump({"diag_error": repr(exc)}, f, ensure_ascii=False)
                except OSError:
                    pass

        import threading

        threading.Thread(target=_diagnose, daemon=True).start()
        webview.start(debug=False, gui="edgechromium")
    except Exception as exc:  # 例如本机缺少 WebView2 运行时
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0,
            "无法启动 2048 Arena-1：\n%s\n\n请确认系统已安装 Microsoft Edge WebView2 运行时。"
            % exc,
            "2048 Arena-1",
            0x10,  # MB_ICONERROR
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
