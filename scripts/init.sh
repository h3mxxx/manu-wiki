#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
mkdir -p .secrets
chmod 700 .secrets
if [[ ! -e .env ]]; then cp .env.example .env; fi
if [[ ! -e .secrets/db_password ]]; then
  python3 - <<'PY'
import secrets
from pathlib import Path
with Path('.secrets/db_password').open('x') as f:
    f.write(secrets.token_hex(32))
PY
fi
if [[ ! -s .secrets/db_password ]]; then
  echo '数据库密码文件为空，请检查；未覆盖已有文件。' >&2
  exit 1
fi
chmod 600 .env .secrets/db_password
docker compose config -q
printf '%s\n' '配置已准备，已有密码保持不变。运行 docker compose up -d。'
