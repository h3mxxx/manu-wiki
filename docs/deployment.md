# 部署与维护

本仓库用于隔离环境的 XWiki POC。当前基线为 XWiki `17.10.15-postgres-tomcat`、PostgreSQL `16.15-bookworm`，Compose 项目名为 `manu-wiki-poc`。使用官方镜像及官方 `*_FILE` 密码入口，数据库不映射宿主端口，Wiki 默认只监听 `127.0.0.1:8080`。

以下命令不用于生产变更、覆盖原库或迁移全部 BWIpedia 数据。云工作区与其中的卷不等于长期服务器；正式使用前需确定主机、访问入口、备份保留策略与负责人。实际验收结果以 `reports/` 中的记录为准。

## 配置与首次启动

需要 Docker Engine、Compose v2、Bash、Python 3；备份还需要宿主机上的 `tar`、`sha256sum`、`mktemp`。预留磁盘空间给数据库、附件、镜像与本地备份；内存需求随扩展、附件和索引量增长。

在仓库根目录执行：

```bash
./scripts/init.sh
```

初始化只在文件缺失时创建 `.env` 和 `.secrets/db_password`，不覆盖已有密码。`.env` 与密码文件权限为 `0600`，密钥目录为 `0700`。不要提交这些文件，也不要把 `docker compose config` 的完整输出公开。

`.env.example` 固定了镜像版本、项目名与默认地址。更换项目名会切换到另一组命名卷；不要把它当作日常重命名。数据库初始化后，单独修改密码文件不会同步修改 PostgreSQL 中的密码，需另行制定密码轮换步骤。

### 普通主机

普通主机直接使用 `compose.yaml`：

```bash
unset COMPOSE_FILE
docker compose config -q
docker compose pull
docker compose up -d
docker compose ps
```

### 当前受管云环境

此环境访问扩展仓库需要 Java HTTP/HTTPS 代理及云环境 CA 信任库。额外的 `compose.cloud.yaml` 为 XWiki 设置代理参数，并只读挂载 `.runtime/java-cacerts`。它们包含环境专属配置，已被 Git 忽略；普通主机不需要照抄。

首次在同类云环境中生成配置：先 `docker compose -f compose.yaml up -d` 启动基础容器，再运行 `./scripts/configure-cloud.sh`。该脚本复制镜像自带信任库并导入环境 CA，读取容器的已配置代理主机，生成本地 override；不关闭 TLS 验证。需要宿主提供 `keytool` 和 `CODEX_PROXY_CERT`，普通主机不执行。新的云会话若代理地址改变，先核对环境配置并重新生成。

在当前云环境，每次进入新的 shell，先选择两个配置文件，后续所有 Compose 操作和备份脚本都继承这一设置：

```bash
export COMPOSE_FILE=compose.yaml:compose.cloud.yaml
docker compose config -q
docker compose up -d
docker compose ps
```

等价启动命令为 `docker compose -f compose.yaml -f compose.cloud.yaml up -d`。只有命令行 `-f` 不会传给备份脚本，运行脚本时仍需设置 `COMPOSE_FILE`。不要在云环境用仅含 `compose.yaml` 的 `up` 重建应用，否则会丢失代理及信任库挂载。工作区重建后应按新环境重新生成云配置；旧代理地址和 CA 文件不保证适用。

启动后访问本机 `http://127.0.0.1:8080/`，按官方 Distribution Wizard 完成标准发行版安装和管理员创建。首次下载扩展和建立索引可能需要数分钟。远程运维可使用 SSH 本地转发访问回环端口；团队共享入口应另行配置 HTTPS、域名和访问控制，不能把修改绑定地址当作已经完成安全部署。

## 日常检查与停止

先按上节选好当前环境的 `COMPOSE_FILE`，在仓库根目录执行：

```bash
docker compose ps
docker compose logs --tail=100 xwiki db
curl -fsS --max-time 15 http://127.0.0.1:8080/bin/view/Main/ >/dev/null
docker system df
df -h .
```

HTTP 成功和容器健康只能证明服务有响应。还应使用测试账号确认登录、页面读取、附件下载和搜索；定期检查只读用户及匿名用户无法读取草稿。日志可能包含页面内容、账号或连接信息，分享前先脱敏。

```bash
# 暂停应用，保留数据库运行。
docker compose stop xwiki
docker compose start xwiki

# 暂停整个 POC，保留全部卷。
docker compose stop
docker compose start
```

不要执行 `docker compose down -v`、`docker volume prune`，也不要删除卷目录。这些操作可能永久移除数据库或附件。停止和启动不清空数据；重新创建容器时，保持项目名和命名卷不变。

| 存储位置 | 内容 | 处理方式 |
| --- | --- | --- |
| `postgres_data` 命名卷 | 页面、用户、权限、版本及扩展相关数据库记录 | 使用 `pg_dump`，不直接打包运行中的数据库目录 |
| `xwiki_data` 命名卷，容器路径 `/usr/local/xwiki` | 永久目录，含文件存储、附件、扩展与索引等 | 停止 XWiki 后归档，并与同次数据库备份一起保存 |
| `.secrets/`、`.env`、Compose 文件 | 密钥和部署配置 | 限制读取权限，与备份一起保护 |
| `.runtime/java-cacerts`、`compose.cloud.yaml` | 当前云环境信任库与代理设置 | 环境专属；迁移时重新核对 |

卷的实际名称通常为 `manu-wiki-poc_postgres_data` 和 `manu-wiki-poc_xwiki_data`，以 Docker 检查结果为准。

## 一致性备份

备份安排在短暂维护窗口。执行期间不要修改配置、手动启动 XWiki，或通过其他程序直接写数据库。脚本要求 `db`、`xwiki` 各有一个运行中的容器；不会备份一个原本停止的项目。

```bash
# 普通主机
unset COMPOSE_FILE
./scripts/backup.sh

# 当前云环境；默认输出至仓库 backups/。
COMPOSE_FILE=compose.yaml:compose.cloud.yaml ./scripts/backup.sh

# 可指定备份父目录；相对路径相对于调用脚本时的目录。
COMPOSE_FILE=compose.yaml:compose.cloud.yaml ./scripts/backup.sh /workspace/wiki-backups
```

脚本通过 Compose 停止 XWiki，保持 PostgreSQL 运行，再生成 `pg_dump -Fc` 数据库备份，并用本机已有 PostgreSQL 镜像只读挂载 XWiki 卷进行归档。助手容器不联网。退出时会尝试重新启动 XWiki；如果恢复启动失败，脚本返回错误并输出手动启动提示。`SIGKILL`、断电和 Docker daemon 故障无法由 shell 的退出清理处理，此时应手动检查服务。

每次备份创建独立目录，目录权限为 `0700`，文件默认 `0600`，不覆盖旧备份：

- `database.dump`：PostgreSQL 自定义格式备份。
- `xwiki.tar.gz`：XWiki 永久目录，保留数字 UID/GID。
- `config.tar.gz`：`compose.yaml`、`.env`、`.secrets/`，以及存在时的云 override 与 Java 信任库。
- `images.txt`、`manifest.txt`：源镜像标签及本机镜像 ID、项目名、UTC 时间和配置文件选择。
- `SHA256SUMS`：上述文件的 SHA-256 校验值。

`*.partial` 目录表示未完成，不能用于恢复。脚本不会自动删除失败产物或过期备份；保留与清理应由负责人按已批准策略执行。`.runtime/backup.lock` 防止同仓库并行执行；异常断电后，只有确认没有备份进程时才能手动移除这个空锁目录。

脚本打包本仓库约定的配置文件；如果新增了其他 `COMPOSE_FILE` override、外部密钥或挂载，应先扩展备份清单。归档内含数据库密码，数据库和附件可能包含业务数据。备份保留在当前云工作区仍有共同丢失风险，应另存一份到经授权的受控存储；权限位不是加密，跨主机传输及长期保存还需受控通道和加密。

备份后检查应用恢复运行，并核对完整性：

```bash
docker compose ps
curl -fsS --max-time 15 http://127.0.0.1:8080/bin/view/Main/ >/dev/null
cd /absolute/path/to/one-completed-backup
sha256sum -c SHA256SUMS
tar -tzf xwiki.tar.gz >/dev/null
tar -tzf config.tar.gz >/dev/null
```

校验成功只说明文件未变且归档可读。完整验收需要在独立实例演练恢复，并验证页面、历史、权限与附件均存在。

## 恢复到全新项目

恢复使用新的目录、项目名、端口和全新卷，不覆盖或停止原项目。必须使用同一次完整备份中的数据库和 XWiki 永久目录；保留原密钥及配置。先使用备份时相同的镜像版本恢复，确认成功后再讨论升级。

下面示例适用于本仓库当前的两个服务和卷名。在 Bash 中执行，先替换 `backup` 和 `restore_parent`。`restore_parent` 必须是已存在、可写且适合保留恢复实例的目录。示例端口为 `127.0.0.1:18080`，与原项目的 `8080` 分离。

```bash
(
  set -euo pipefail
  umask 077
  backup=/absolute/path/to/one-completed-backup
  restore_parent=/workspace
  test -s "$backup/SHA256SUMS"
  (cd "$backup" && sha256sum -c SHA256SUMS)

  restore_dir=$(mktemp -d "$restore_parent/manu-wiki-restore.XXXXXX")
  tar -xzf "$backup/config.tar.gz" -C "$restore_dir"
  cd "$restore_dir"

  # shell 环境优先于归档中的 .env，确保使用新项目与独立端口。
  export COMPOSE_PROJECT_NAME="manu-wiki-restore-$(date -u +%Y%m%d%H%M%S)-$$"
  export XWIKI_BIND_ADDRESS=127.0.0.1
  export XWIKI_PORT=18080

  # 普通主机保留此行；当前云环境须把它替换成下一行。
  unset COMPOSE_FILE
  # export COMPOSE_FILE=compose.yaml:compose.cloud.yaml

  docker compose config -q
  test -z "$(docker compose ps -aq)"
  for suffix in postgres_data xwiki_data; do
    if docker volume inspect "${COMPOSE_PROJECT_NAME}_${suffix}" >/dev/null 2>&1; then
      echo '目标卷已存在；停止恢复，改用新的项目名。' >&2
      exit 1
    fi
  done

  # 只先启动全新数据库。此时不要启动 XWiki。
  docker compose up -d --wait --wait-timeout 120 db
  docker compose exec -T db pg_restore \
    --username=xwiki --dbname=xwiki --no-owner --exit-on-error \
    < "$backup/database.dump"

  # 新建 XWiki 卷并恢复文件，首次启动应用前完成两份数据的恢复。
  restored_volume="${COMPOSE_PROJECT_NAME}_xwiki_data"
  docker volume create \
    --label "com.docker.compose.project=$COMPOSE_PROJECT_NAME" \
    --label com.docker.compose.volume=xwiki_data \
    "$restored_volume" >/dev/null
  db_id=$(docker compose ps -q db)
  postgres_image_id=$(docker inspect --format '{{.Image}}' "$db_id")
  docker run --rm -i --network none --read-only \
    --mount "type=volume,source=$restored_volume,target=/restore,volume-nocopy" \
    --entrypoint tar "$postgres_image_id" \
    --numeric-owner -xzf - -C /restore < "$backup/xwiki.tar.gz"

  docker compose up -d --wait --wait-timeout 600 xwiki
  docker compose ps
  printf '恢复实例目录：%s\n新项目名：%s\n' "$restore_dir" "$COMPOSE_PROJECT_NAME"
)
```

若在当前云环境恢复，先核对归档的代理地址和信任库仍适用，并启用示例中的 `COMPOSE_FILE` 行。其他主机应按当地网络条件使用普通配置或准备自己的 override。恢复失败时，原项目不受此流程影响；保留新实例和错误信息用于排查，不要把失败数据反向写回原项目。

访问 `http://127.0.0.1:18080/`，使用备份时已有的账号检查页面数量、页面历史、已知附件及其校验值、阅读权限、草稿隔离和搜索。演练实例含真实账号及内容，只开放回环地址；测试出站邮件、Webhook 或外部集成前先检查恢复的配置，避免触发业务动作。

例子中的新项目名通过 shell 环境覆盖 `.env`，子 shell 退出后不会保存。后续维护恢复实例时，进入输出目录，重新设置同一个 `COMPOSE_PROJECT_NAME`、`XWIKI_PORT=18080` 和相应的 `COMPOSE_FILE`，或只修改该恢复目录的 `.env` 固定这两个值。切勿在恢复目录直接使用原来的项目名运行 `up`。

## 升级与故障定位

升级先在独立恢复实例上演练：检查目标 XWiki 与扩展、PostgreSQL 的兼容要求，保存当前镜像记录，生成可恢复备份，再修改镜像版本并执行 Compose 更新。XWiki 可能迁移数据库结构；出现问题时不能仅切回旧镜像，应恢复升级前同一时间点的数据库和永久目录。PostgreSQL 大版本升级不能直接把原数据卷交给新大版本镜像。

| 现象 | 先检查 |
| --- | --- |
| `db` 不健康 | 数据库日志、磁盘空间、卷权限；不要删除卷“重装” |
| Wiki 长时间未就绪 | XWiki 日志、初始化进度、内存；首次扩展安装与索引可能较慢 |
| 扩展下载失败或 TLS 报错 | 当前云环境是否选了双 Compose 配置、代理是否可达、Java 信任库是否挂载；不要关闭 TLS 校验 |
| 密码文件改后无法连接 | 文件与已初始化数据库中的角色密码是否一致 |
| 页面存在但附件异常 | 是否只恢复了数据库、永久目录归档是否匹配、文件所有权是否保留 |
| 重建后像全新 Wiki | 项目名、卷名和 Compose 文件选择是否改变；先核对原卷，不初始化覆盖 |

未经恢复演练、权限验收和长期存储安排的 POC 不代表生产部署已经完成。
