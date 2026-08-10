# 贡献指南（Contributing）

感谢你对 **2048 Arena-1** 的兴趣！任何形式的贡献（代码、文档、Issue、建议）都欢迎。

## 开发流程

1. **Fork** 本仓库并克隆到本地
2. 创建功能分支：`git checkout -b feature/xxx`（或 `fix/xxx`）
3. 编写 / 修改代码
4. **确保通过测试**（见下）
5. 提交：`git commit`（建议遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/) 风格）
6. 推送分支并提交 **Pull Request**，说明改动内容与测试结果

## 本地测试

```bash
# 依赖
pip install -r requirements.txt

# 核心逻辑 + AI 单元测试（Node，需 Node 18+）
node tools/test_logic.js

# 界面冒烟测试（会短暂弹出窗口，自动关闭）
python tools/smoke_test.py
```

PR 触发 CI 时也会自动运行 `node tools/test_logic.js`。

## 代码风格

- **JavaScript（浏览器 / Node 共用）**：遵循项目内既有风格（2 空格缩进、单引号、显式注释）；核心逻辑保持**纯函数、无 DOM 依赖**，便于测试
- **Python**：PEP 8，函数带 docstring
- 新增功能请尽量附带单元测试（`tools/test_logic.js`）

## 架构速览

- `game/assets/logic.js`：纯逻辑 + AI（浏览器与 Node 共用，**不要在这里写 DOM 代码**）
- `game/assets/index.html`：界面、动画、交互、持久化桥接
- `game/app.py`：pywebview 窗口与本地存储桥接 API
- `build.py`：PyInstaller 一键打包

## Issue 模板要点

- 描述复现步骤、预期行为与实际行为
- 附上系统版本（Windows 版本）与运行方式（exe / 源码）
- Bug 类问题请附 `%APPDATA%\ZCode2048\state.json` 内容（如涉及持久化）

## 许可证

提交代码即表示同意在 [MIT](LICENSE) 许可证下发布。
