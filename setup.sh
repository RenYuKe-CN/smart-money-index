#!/usr/bin/env bash
set -euo pipefail
echo "=== Smart Money Index — Setup ==="
echo ""
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入 CLAWBY_API_KEY"
    exit 0
fi
echo "🚀 启动服务..."
docker compose up -d --build
echo ""
echo "✅ 启动完成！"
echo "   前端: http://localhost:3002"
echo "   后端: http://localhost:8002"
