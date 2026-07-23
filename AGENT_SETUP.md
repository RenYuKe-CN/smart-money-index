# Smart Money Index — Agent Setup Guide

将该提示词复制给你的 Codex agent，她会自动在本地安装并运行 Smart Money Index 项目。

---

## Prompt（复制以下内容给 agent）

```
请帮我完成以下步骤，在本地安装并运行 Smart Money Index 项目：

## Step 1: 克隆仓库

```bash
git clone https://github.com/RenYuKe-CN/smart-money-index.git
cd smart-money-index
```

## Step 2: 配置环境变量

```bash
cp .env.example backend/.env
```

编辑 `backend/.env`，将 `CLAWBY_API_KEY` 改为你在 https://www.openclawby.com/ 注册获取的真实 API Key。

## Step 3: 安装后端依赖并启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002 &
```

确认后端启动成功：`curl http://localhost:8002/api/health` 应返回 `{"status":"ok"}`。

## Step 4: 安装前端依赖并启动

```bash
cd frontend
npm install
npx next dev --port 3002 &
```

确认前端启动成功：浏览器打开 `http://localhost:3002`。

## Step 5: 验证

1. 浏览器打开 `http://localhost:3002`
2. 页面应显示 AAPL 的 SMI 仪表盘，包含价格、6 维分解、历史走势图
3. 侧边栏 Watchlist 显示多个 ticker 的 SMI 分数
4. 点击「刷新」按钮可强制重新拉取数据
5. 点「编辑」按钮可修改 Watchlist

## 注意事项

- 如果没有 Clawby API Key，系统会自动使用 Demo 数据运行，数据基于 ticker 种子生成
- Clawby 免费版有 20 次/分钟的速率限制，批量请求超出部分自动回退 Demo
- 后端端口 8002，前端端口 3002，可在 `backend/.env` 中修改
- 前端通过 `NEXT_PUBLIC_API_URL` 环境变量连接后端，默认 `http://localhost:8002`
```

---

## 快速参考

| 项目 | 路径 |
|---|---|
| 仓库 | `https://github.com/RenYuKe-CN/smart-money-index` |
| 后端端口 | 8002 |
| 前端端口 | 3002 |
| 健康检查 | `http://localhost:8002/api/health` |
| API Key 注册 | [openclawby.com](https://www.openclawby.com/) |
| 本地 .env | `backend/.env` |

## 架构

```
frontend:3002  ──API──▶  backend:8002  ──HTTP──▶  api.openclawby.com
                                                      │
                                               ┌──────┴──────┐
                                               │  真实数据     │
                                               │  (API Key)   │
                                               └──────────────┘
```

没有 API Key 或网络不可用时，后端自动使用 Demo 数据，不影响功能体验。
