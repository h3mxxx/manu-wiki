#!/usr/bin/env bash
# Optional adapter for this managed cloud environment; ordinary servers do not need it.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CODEX_PROXY_CERT:?当前环境没有提供 CODEX_PROXY_CERT，不适用此脚本}"
command -v keytool >/dev/null
mkdir -p .runtime
container_id=$(docker compose -f compose.yaml ps -q xwiki)
[[ -n "$container_id" ]] || { echo '先用基础 compose 启动 xwiki。' >&2; exit 1; }
docker cp "${container_id}:/opt/java/openjdk/lib/security/cacerts" .runtime/java-cacerts
keytool -importcert -noprompt -alias manu-cloud-proxy -file "$CODEX_PROXY_CERT" \
  -keystore .runtime/java-cacerts -storepass changeit >/dev/null
python3 - "$container_id" <<'PY'
import json, subprocess, sys, urllib.parse
from pathlib import Path
raw = subprocess.check_output(['docker', 'inspect', sys.argv[1], '--format', '{{json .Config.Env}}'])
env = dict(item.split('=', 1) for item in json.loads(raw))
proxy = urllib.parse.urlparse(env.get('HTTPS_PROXY', env.get('https_proxy', '')))
if not proxy.hostname or not proxy.port or proxy.username or proxy.password:
    raise SystemExit('需要环境提供不含凭据的容器代理地址；未生成配置。')
if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-' for c in proxy.hostname):
    raise SystemExit('代理主机名格式不支持。')
opts = ('-Xms512m -Xmx2048m -Dfile.encoding=UTF-8 -Djava.awt.headless=true '
        f'-Dhttp.proxyHost={proxy.hostname} -Dhttp.proxyPort={proxy.port} '
        f'-Dhttps.proxyHost={proxy.hostname} -Dhttps.proxyPort={proxy.port} '
        "'-Dhttp.nonProxyHosts=localhost|127.*|db' "
        '-Djavax.net.ssl.trustStore=/run/cloud/java-cacerts '
        '-Djavax.net.ssl.trustStorePassword=changeit')
config = {'services': {'xwiki': {'environment': {'JAVA_OPTS': opts},
          'volumes': ['./.runtime/java-cacerts:/run/cloud/java-cacerts:ro']}}}
Path('compose.cloud.yaml').write_text(json.dumps(config, indent=2) + '\n')
PY
docker compose -f compose.yaml -f compose.cloud.yaml config -q
printf '%s\n' '云配置已生成；请 export COMPOSE_FILE=compose.yaml:compose.cloud.yaml 后 docker compose up -d。'
