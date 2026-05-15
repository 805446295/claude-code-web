# Claude Web Chat

Claude Code 的浏览器界面。**启动即得公网地址**，手机、平板、其他电脑都能打开用。

---

## 三步开始

### 第一步：安装 Claude Code

下载安装 [Trae](https://www.trae.ai)（或其他国产 AI 编程工具），用它一键安装 cloudflare 和 Claude Code 并配置好 API。几分钟搞定。

装好之后，打开终端验证：

```bash
claude --version
```

> Trae 会自动设置好 `ANTHROPIC_AUTH_TOKEN` 环境变量和 PATH，无需手动配置。（有什么没设置好报错了就狠狠的压力trae）

### 第二步：下载项目，安装依赖

```bash
git clone https://github.com/805446295/claude-code-web.git
cd claude-code-web
pip install -r requirements.txt
```

### 第三步：启动

```bash
start.bat
```

启动后终端会打印：

```
  Local:  http://127.0.0.1:5000
  Public URL will appear below:
  =================================
  https://xxx-xxx-xxx.trycloudflare.com
```

浏览器打开 `http://127.0.0.1:5000`，输入密码 `123456`。公网地址发给别人或用手机打开也行。

---

## 功能

- 流式对话，实时看到 Claude 回复
- 可折叠的思考过程 — 能看到 Claude 的推理
- 工具调用可视化 — 文件读写、代码搜索、命令执行等全部可见
- Markdown 渲染
- 多轮对话，上下文连续
- 公网地址自动生成，无需注册、无需配置

## 启动脚本做了什么

1. 从 PATH 找到 `claude`
2. 若没有 `cloudflared`，自动从 GitHub 下载到项目目录
3. 启动 Flask 服务（127.0.0.1:5000）
4. 启动 Cloudflare Tunnel，生成公网地址

## 配置项

| 环境变量 | 说明 | 默认值 |
|---|---|---|
| `ANTHROPIC_AUTH_TOKEN` | API Key（Trae 安装时自动设置） | — |
| `ANTHROPIC_API_KEY` | API Key 的替代方案 | — |
| `CLAUDE_CODE_EXECPATH` | claude 可执行文件路径 | 自动从 PATH 检测 |
| `PORT` | 服务端口 | `5000` |

## 项目结构

```
├── app.py              # Flask 服务端
├── templates/
│   └── index.html      # 前端
├── static/
│   └── marked.min.js   # Markdown 渲染
├── requirements.txt    # Python 依赖
├── start.bat           # Windows 启动脚本
├── start.sh            # macOS/Linux 启动脚本
└── .gitignore
```

## 架构

```
浏览器 ←→ Flask (:5000) ←→ Claude Code CLI ←→ Anthropic API
              │                    │
         SSE 流式传输          stream-json
```

- Flask 为每个会话启动一个 `claude` 子进程
- 消息通过 Server-Sent Events 实时推送
- 对话存在内存中，重启服务即清空

## 安全提示

- 默认密码 `123456` 写在 `app.py` 里，暴露到公网前请改成自己的
- Claude Code 以 `--dangerously-skip-permissions` 运行，能访问此页面的人可以操作本机文件、执行命令
- **仅建议在个人可信网络中使用**
