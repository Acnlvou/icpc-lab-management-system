#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== [1/2] 启动 FastAPI 后端 (http://127.0.0.1:8000) ==="
cd "$ROOT_DIR/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "=== [2/2] 启动 Vue 3 前端 (http://127.0.0.1:5173) ==="
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!

trap 'echo "正在停止前后端服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' EXIT INT TERM
echo "系统已启动：前端 http://127.0.0.1:5173 ｜ 后端 Swagger http://127.0.0.1:8000/docs"
wait
