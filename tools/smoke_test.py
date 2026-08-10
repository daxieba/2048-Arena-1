"""冒烟测试：启动 pywebview 窗口，验证页面加载与游戏初始化，然后自动关闭。

用法：python tools/smoke_test.py
"""
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "game"))
import webview  # noqa: E402


def eval_js_retry(win, js, retries=4, delay=0.6):
    """evaluate_js 在 WebView2 冷启动瞬间偶发返回 None，带重试兜底。"""
    for _ in range(retries):
        v = win.evaluate_js(js)
        if v is not None:
            return v
        time.sleep(delay)
    return None


def main():
    results = {}

    def check(win):
        time.sleep(3.5)  # 等待页面加载与 init 完成
        checks = {
            "logic 加载(move 存在)": "typeof move === 'function'",
            "初始方块=2": "document.querySelectorAll('.tile').length === 2",
            "得分=0": "document.getElementById('score').textContent === '0'",
            "撤销按钮已禁用": "document.getElementById('btnUndo').disabled === true",
            "尺寸选择=4": "document.getElementById('selSize').value === '4'",
            "页面无需滚动": (
                "document.documentElement.scrollHeight <= window.innerHeight"
            ),
        }
        try:
            for name, js in checks.items():
                v = win.evaluate_js(js)
                results[name] = v
            # 依次尝试四个方向，直到出现一次有效移动（初始两子可能贴边导致单方向无移动，
            # 无移动时游戏正确地不推历史、撤销保持禁用）
            dirs = ["left", "up", "right", "down"]
            moved_ok = False
            for d in dirs:
                win.evaluate_js("doMove('%s')" % d)
                time.sleep(0.35)
                tile_count = eval_js_retry(win, "document.querySelectorAll('.tile').length")
                results["%s 移动后 tile 数合理(%r)" % (d, tile_count)] = (
                    tile_count is not None and 1 <= tile_count <= 3
                )
                results["%s 未弹失败框" % d] = (
                    win.evaluate_js("!document.getElementById('mask').classList.contains('show')")
                )
                if win.evaluate_js("!document.getElementById('btnUndo').disabled"):
                    moved_ok = True
                    dump = win.evaluate_js(
                        "JSON.stringify({tiles: state.tiles.map(t=>({v:t.value,r:t.r,c:t.c,d:t.dead})),"
                        " hist: state.history.length, moving: moving, score: state.score})"
                    )
                    print("   [诊断] 移动后内部状态(" + d + "): " + dump)
                    break
            results["至少一次有效移动"] = moved_ok
            results["撤销按钮已可用"] = moved_ok
            # 撤销后恢复 2 个初始块
            win.evaluate_js("undo()")
            time.sleep(0.2)
            results["撤销后 tile 数=2"] = (
                win.evaluate_js("document.querySelectorAll('.tile').length === 2")
            )
            # AI 自动玩：开启后 3 秒一次移动，等 4 秒应至少发生一次移动（历史非空）
            win.evaluate_js("startAi()")
            time.sleep(1)
            results["AI 按钮变为停止"] = (
                win.evaluate_js("document.getElementById('btnAi').classList.contains('ai-running')")
            )
            time.sleep(4)
            ai_hist = eval_js_retry(win, "state.history.length")
            results["AI 4 秒内发生移动(hist=%r)" % ai_hist] = (
                ai_hist is not None and ai_hist >= 1
            )
            win.evaluate_js("stopAi()")
            time.sleep(0.3)
            results["AI 停止后按钮恢复"] = (
                win.evaluate_js("!document.getElementById('btnAi').classList.contains('ai-running')")
            )
            # 排行榜：初始渲染 5 行空位；模拟一局成绩后应出现记录且排序正确
            results["玩家榜初始 5 行"] = (
                win.evaluate_js("document.querySelectorAll('#rankPlayer .rank-row').length === 5")
            )
            win.evaluate_js(
                "state.score = 120; state.tiles = [{value:64,r:0,c:0,dead:false}];"
                "state.aiOn = false; recordScore();"
            )
            time.sleep(0.2)
            results["玩家榜有成绩(120)"] = (
                win.evaluate_js(
                    "state.leaderboard.player.length === 1 && state.leaderboard.player[0].score === 120"
                )
            )
            results["玩家榜渲染第一行=120"] = (
                win.evaluate_js(
                    "document.querySelector('#rankPlayer .rank-row .rs').textContent === '120'"
                )
            )
            results["AI 榜保持为空"] = (
                win.evaluate_js("state.leaderboard.ai.length === 0")
            )
            # 还原状态，避免影响后续断言
            win.evaluate_js("state.score = 0; state.tiles = [];")
            # pywebview 桥接可用（load_state 不抛异常）
            try:
                bridge = win.evaluate_js("window.pywebview && window.pywebview.api ? 'ok' : 'missing'")
                results["pywebview 桥接(" + bridge + ")"] = bridge == "ok"
            except Exception:  # noqa: BLE001
                results["pywebview 桥接"] = False
        except Exception as exc:  # noqa: BLE001
            results["EXCEPTION"] = repr(exc)
        finally:
            win.destroy()

    win = webview.create_window(
        "2048 冒烟测试",
        os.path.join(ROOT, "game", "assets", "index.html"),
        width=520,
        height=780,
    )
    webview.start(check, win, debug=False, gui="edgechromium")

    ok = True
    for name, v in results.items():
        if v is True:
            print("  ✓", name)
        else:
            ok = False
            print("  ✗", name, "=>", v)
    print("\n冒烟测试：" + ("通过" if ok else "失败"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
