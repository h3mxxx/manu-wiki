#!/usr/bin/env bash
# Back up the repository's Compose project; inherit COMPOSE_FILE for overrides.
set -euo pipefail
umask 077

usage() {
  cat <<'EOF'
用法：scripts/backup.sh [备份父目录]

默认输出到仓库的 backups/，每次创建独立目录，不覆盖旧备份。
运行期间会停止 XWiki；数据库保持运行。退出时尝试重新启动 XWiki。
要求 db 和 xwiki 均已运行，且没有其他操作者同时改配置或启动应用。

普通主机：unset COMPOSE_FILE; ./scripts/backup.sh
当前云环境：COMPOSE_FILE=compose.yaml:compose.cloud.yaml ./scripts/backup.sh

备份包含数据库、附件、配置与密钥；请按敏感数据保管。
EOF
}

if [[ ${1:-} == -h || ${1:-} == --help ]]; then
  usage
  exit 0
fi
if (( $# > 1 )) || [[ ${1:-} == -* ]]; then
  usage >&2
  exit 2
fi

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
# Resolve an explicitly supplied relative destination against the caller's cwd.
backup_root=${1:-"$project_dir/backups"}
mkdir -p -- "$backup_root"
backup_root=$(cd -- "$backup_root" && pwd -P)
cd -- "$project_dir"
compose=(docker compose --project-directory "$project_dir")

for command_name in docker tar sha256sum mktemp; do
  command -v "$command_name" >/dev/null || {
    printf '缺少命令：%s\n' "$command_name" >&2
    exit 1
  }
done
[[ -s .env && -s .secrets/db_password ]] || {
  printf '%s\n' '缺少 .env 或数据库密码文件；未停止服务。' >&2
  exit 1
}
"${compose[@]}" config -q

db_id=$("${compose[@]}" ps --status running -q db)
xwiki_id=$("${compose[@]}" ps --status running -q xwiki)
if [[ -z $db_id || -z $xwiki_id || $db_id == *$'\n'* || $xwiki_id == *$'\n'* ]]; then
  printf '%s\n' '要求 db 和 xwiki 各有一个运行中的容器；未停止服务。' >&2
  exit 1
fi
mount_info=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/usr/local/xwiki"}}{{.Type}} {{.Name}}{{end}}{{end}}' "$xwiki_id")
[[ $mount_info == 'volume '* && -n ${mount_info#volume } ]] || {
  printf '%s\n' '未找到 XWiki 的永久命名卷；未停止服务。' >&2
  exit 1
}
xwiki_volume=${mount_info#volume }
postgres_image_id=$(docker inspect --format '{{.Image}}' "$db_id")
project_name=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$xwiki_id")

mkdir -p .runtime
lock_dir="$project_dir/.runtime/backup.lock"
if ! mkdir -- "$lock_dir" 2>/dev/null; then
  printf '%s\n' '备份锁已存在；请先确认没有备份进程运行。未停止服务。' >&2
  exit 1
fi

restart_needed=0
backup_dir=''
backup_complete=0
cleanup() {
  local status=$?
  trap - EXIT INT TERM
  if (( restart_needed )); then
    if ! "${compose[@]}" start xwiki; then
      printf '%s\n' '错误：未能重新启动 XWiki，请使用相同 COMPOSE_FILE 手动运行 docker compose start xwiki。' >&2
      status=1
    fi
  fi
  rmdir -- "$lock_dir" || status=1
  if (( ! backup_complete )) && [[ -n $backup_dir ]]; then
    printf '备份未完成，请勿用于恢复：%s\n' "$backup_dir" >&2
  fi
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

backup_dir=$(mktemp -d "$backup_root/$(date -u +%Y%m%dT%H%M%SZ).XXXXXX.partial")
config_paths=(compose.yaml .env .secrets)
[[ ! -f compose.cloud.yaml ]] || config_paths+=(compose.cloud.yaml)
[[ ! -f .runtime/java-cacerts ]] || config_paths+=(.runtime/java-cacerts)
tar -czf "$backup_dir/config.tar.gz" -- "${config_paths[@]}"
docker inspect --format '{{.Config.Image}} {{.Image}}' "$db_id" "$xwiki_id" > "$backup_dir/images.txt"
printf 'project=%s\ncreated_utc=%s\nxwiki_volume=%s\ncompose_file=%s\n' \
  "$project_name" "$(date -u +%FT%TZ)" "$xwiki_volume" "${COMPOSE_FILE:-compose.yaml}" > "$backup_dir/manifest.txt"

printf '%s\n' '正在停止 XWiki，以备份同一时间点的数据库与附件。'
restart_needed=1
"${compose[@]}" stop --timeout 60 xwiki
"${compose[@]}" exec -T db pg_dump --username=xwiki --dbname=xwiki --format=custom > "$backup_dir/database.dump"
# Reuse the local PostgreSQL image; the helper has no network and reads the volume only.
docker run --rm --network none --read-only \
  --mount "type=volume,source=$xwiki_volume,target=/source,readonly" \
  --entrypoint tar "$postgres_image_id" \
  --numeric-owner -czf - -C /source . > "$backup_dir/xwiki.tar.gz"
[[ -s $backup_dir/database.dump && -s $backup_dir/xwiki.tar.gz ]]

(
  cd -- "$backup_dir"
  sha256sum database.dump xwiki.tar.gz config.tar.gz images.txt manifest.txt > SHA256SUMS
)
final_dir=${backup_dir%.partial}
[[ ! -e $final_dir ]]
mv -- "$backup_dir" "$final_dir"
backup_dir=$final_dir
backup_complete=1
printf '备份文件已完成：%s\n' "$backup_dir"
printf '%s\n' '退出前将重新启动 XWiki；随后请检查 docker compose ps 和 HTTP 响应。'
