# Smart Money Index (聪明钱指数)

将 Clawby 六个维度的数据压缩成一个 0-100 指数，一眼判断机构对某只股票的真实态度。

## 核心概念

```
散户看 K 线 → 发现涨了 → 追涨
机构看暗池 + 期权 + 做空 → 发现资金在逆向流 → 提前布局
            ↑
      聪明钱指数让你看到这个
```

## 六维加权公式

| 维度 | 权重 | 说明 |
|---|---|---|
| 暗池净流 (Dark Pool) | 25% | 大单在暗池的集中度 |
| 短仓趋势 (Short Volume) | 20% | 空头在加仓还是撤退 |
| 期权偏度 (Options Skew) | 20% | Call/Put 持仓比 |
| 借券费率 (Borrow Fee) | 15% | 做空成本高低 |
| Reddit 情绪 | 10% | 社交热度变化趋势 |
| 大小单 (Flow Split) | 10% | 机构 vs 散户成交比 |

## 技术栈

- **后端**: Python FastAPI + httpx + uvicorn
- **前端**: Next.js 14 + React 18 + Recharts + Tailwind CSS
- **数据**: Clawby API（真实市场数据，无网络时自动回退 Demo）

## 快速开始

### 1. 获取 Clawby API Key

在 [openclawby.com](https://www.openclawby.com/) 免费注册获取 API Key。

### 2. 配置

```bash
cp .env.example backend/.env
# 编辑 backend/.env，填入你的 API Key
```

### 3. Docker 启动

```bash
docker compose up -d
```

前端 `http://localhost:3002`，后端 `http://localhost:8002`。

### 4. 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# 前端
cd frontend
npm install
npm run dev -- --port 3002
```

## 项目结构

```
smi/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI 入口
│       ├── config.py            # 配置（pydantic-settings）
│       ├── routers/
│       │   ├── smi.py           # SMI API 路由
│       │   ├── config.py        # 配置路由
│       │   └── health.py        # 健康检查
│       ├── services/
│       │   ├── clawby.py        # Clawby API 客户端
│       │   ├── config_store.py   # 本地配置存储
│       │   └── smi/
│       │       ├── engine.py     # SMI 计算引擎
│       │       ├── scanner.py    # 市场扫描器
│       │       ├── signal.py     # 信号检测 + 历史
│       │       └── calculators/  # 6 个维度计算器
│       └── models/schemas.py    # Pydantic 模型
└── frontend/
    └── src/
        ├── app/                 # Next.js 页面
        └── components/
            ├── dashboard/       # 仪表盘组件
            └── layout/          # 侧边栏 + 顶栏
```

## API 端点

| 路径 | 说明 |
|---|---|
| `GET /api/smi/{ticker}` | 获取单只股票 SMI |
| `GET /api/smi/{ticker}/detail` | 获取详情（含历史） |
| `GET /api/smi/{ticker}/detail?refresh=true` | 强制刷新缓存 |
| `POST /api/smi/batch` | 批量获取多个 SMI |
| `GET /api/scanner` | 市场扫描 |
| `GET /api/smi/market-overview` | 市场概况 |
| `GET /api/config` | 获取配置 |
| `PUT /api/config/watchlist` | 更新自选列表 |

## 免费计划限制

Clawby API 免费版每分钟 20 次调用。首次加载时 Sidebar 的批量请求可能超出限制，
超出部分会自动回退到 Demo 数据（基于 Ticker 种子生成，数据有差异性）。
点击「刷新」按钮可单只强制重新拉取。

## License

MIT
