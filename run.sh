#!/bin/bash
# ─────────────────────────────────────────────────────────
# NumbersAuto Pipeline Monitor — 통합 실행 스크립트
# 
# 사용법: ./run.sh
# 자동으로 FastAPI, Vite 서버 시작 + 브라우저 열기
# Ctrl+C로 모든 프로세스 종료
# ─────────────────────────────────────────────────────────

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=5172

echo ""
echo "  ┌──────────────────────────────────────────┐"
echo "  │   NumbersAuto Pipeline Monitor            │"
echo "  │   모니터링 대시보드를 시작합니다            │"
echo "  └──────────────────────────────────────────┘"
echo ""

# Cleanup on exit
cleanup() {
    echo ""
    echo "  🛑 서버를 종료합니다..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "  ✅ 종료 완료"
}
trap cleanup EXIT INT TERM

# ── 1. Start Backend (FastAPI) ──────────────────────────
echo "  🚀 Backend 서버 시작 (port $BACKEND_PORT)..."
cd "$PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT/app/server:$PYTHONPATH" python3 -m uvicorn app.server.main:app --port $BACKEND_PORT --log-level warning &
BACKEND_PID=$!
sleep 1

# Check if backend started
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "  ❌ Backend 시작 실패"
    exit 1
fi
echo "  ✅ Backend: http://localhost:$BACKEND_PORT"

# ── 2. Start Frontend (Vite) ───────────────────────────
echo "  🚀 Frontend 서버 시작..."
cd "$PROJECT_ROOT/app/web"
npx vite --port $FRONTEND_PORT --strictPort 2>/dev/null &
FRONTEND_PID=$!
sleep 2

# Find the actual port (may differ if 5173 is busy)
ACTUAL_URL="http://localhost:$FRONTEND_PORT"
echo "  ✅ Frontend: $ACTUAL_URL"

# ── 3. Open browser ────────────────────────────────────
echo ""
echo "  🌐 브라우저를 엽니다..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$ACTUAL_URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$ACTUAL_URL" 2>/dev/null
fi

echo ""
echo "  ──────────────────────────────────────────"
echo "  📊 대시보드:  $ACTUAL_URL"
echo "  🔌 API:       http://localhost:$BACKEND_PORT/api/runs"
echo "  ──────────────────────────────────────────"
echo "  Ctrl+C로 종료"
echo ""

# Wait for either process to exit
wait
