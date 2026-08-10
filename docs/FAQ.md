# 常见问题（FAQ）

## 安装与运行

**Q: 双击 exe 提示缺少 WebView2 运行时？**
A: 游戏基于 WebView2（EdgeChromium）渲染。Windows 10/11 一般自带；若提示缺失，请到 [Microsoft WebView2 官方下载页](https://developer.microsoft.com/microsoft-edge/webview2/) 安装 Evergreen 运行时（免费），然后重开游戏。

**Q: exe 需要联网吗？**
A: 不需要。exe 完全离线运行，所有资源（界面、逻辑、音效）均已内嵌。

**Q: 支持 macOS / Linux 吗？**
A: 当前 v0.1 仅支持 Windows。路线图已规划跨平台支持。

## 游戏与功能

**Q: 最高分 / 排行榜存在哪里？**
A: `%APPDATA%\ZCode2048\state.json`。删除该文件即可重置所有偏好与排行榜。

**Q: 为什么 AI 自动玩的时候不能手动操作？**
A: 设计如此——AI 接管期间屏蔽手动输入，避免两者互相干扰；点击"⏹ 停止"即可恢复手动。

**Q: AI 自动玩的成绩会进排行榜吗？**
A: 会，进 **AI 榜**（与玩家榜分开，各 5 名）。手动操作的成绩进玩家榜。

**Q: 换棋盘尺寸会丢失当前进度吗？**
A: 会，切换尺寸会开启新的一局（有二次确认）。得分与排行榜不受影响。

**Q: 合成 2048 后游戏就结束了吗？**
A: 不会。胜利弹窗可选"继续游戏"，继续挑战更高分；真正的结束是棋盘无路可走。

**Q: 撤销可以撤销几步？**
A: 最多 100 步（每次有效移动前自动快照）。

## 开发与构建

**Q: 重新打包 exe 的步骤？**
A: `pip install -r requirements.txt` 后执行 `python build.py`，产物在 `dist/2048.exe`。

**Q: 如何运行测试？**
A:
```bash
node tools/test_logic.js     # 逻辑 + AI 单元测试
python tools/smoke_test.py   # 界面冒烟测试
python tools/verify_exe.py   # exe 验证
```

**Q: 遇到 bug 如何反馈？**
A: 请到 [Issues](../../issues) 提交，附上：系统版本、exe 或源码运行方式、复现步骤、`%APPDATA%\ZCode2048\state.json` 内容（如需）。
