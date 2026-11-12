# 首次安装记录与离线恢复

记录时间：2026-11-12（UTC）。环境为官方 XWiki `17.10.15-postgres-tomcat` 镜像与 PostgreSQL 16，安装目标为同版本 Standard Flavor。当前云环境的 Java 代理和 CA 信任库配置见 [部署与维护](deployment.md)。

## 已确认的下载延迟

安装向导在解析 Grizzly、Tyrus 依赖时曾多次停留约半分钟。任务日志确认，部分依赖的 POM 引入了旧仓库 `maven.java.net`；这些仓库返回 HTTP 503，随后才回退至可访问的 XWiki Nexus 仓库。

| 日志中的仓库 | 受影响的已观察依赖 | 结果 |
| --- | --- | --- |
| `jvnet-nexus-releases`：`https://maven.java.net/content/repositories/releases/` | `grizzly-framework:2.3.25`、`grizzly-http-server:2.3.25`、`tyrus-client:1.13.1` | HTTP 503 |
| `jvnet-nexus-snapshots`：`https://maven.java.net/content/repositories/snapshots` | `grizzly-http:2.3.25` | HTTP 503 |

本次最小复现分别请求 releases 下的 `grizzly-framework-2.3.25.pom` 和 snapshots 下的 `grizzly-http-2.3.25.pom`，均在约 0.06–0.08 秒返回 HTTP 503，正文为 `upstream connect error or disconnect/reset before headers. reset reason: remote connection failure`。这说明当前网络路径无法连接该旧仓库；尚未区分旧站点本身故障与代理至上游连接故障。

同一环境访问 XWiki Nexus 中的 `grizzly-http-2.3.25.pom` 及 SHA-1 文件返回 HTTP 200。使用 `XWikiExtensionManager` User-Agent 和压缩请求头访问该 POM 也成功。不能据此把延迟归因于 XWiki Nexus 不可用。

镜像使用 Maven Resolver `1.9.24`。线程栈显示下载线程位于 `ServiceUnavailableRetryExec` 的等待阶段；对应版本默认对 HTTP 429、503 重试 3 次，无 `Retry-After` 时分别等待 5、10、15 秒。若响应带有该头则遵守其等待时间，单次上限为 5 分钟。任务日志中的 503 和约 30 秒间隔与这一机制一致。

可复核的容器内位置：

- 安装任务日志：`/usr/local/xwiki/data/jobs/status/3/extension/action/org.xwiki.platform%3Axwiki-platform-distribution-flavor-mainwiki/wiki%3Axwiki/log.xml`。
- 下载临时目录：`/usr/local/tomcat/work/Catalina/localhost/ROOT/xwiki-temp/extension/download/`。其中 `repository*` 子目录为临时会话仓库，不能当作持久扩展缓存。

## 当前状态

记录时，向导已越过上述依赖解析，进入 `org.xwiki.contrib:webjar-blueimp-gallery:3.4.0` 的扩展下载。因此继续观察正在进行的安装，尚未为这些延迟重启应用或导入离线包。本记录不代表 Standard Flavor 已安装完成；最终状态以实际向导及验收记录为准。

备用官方 XIP 已下载到当前工作区的 `/tmp/manu-standard-17.10.15.xip`，**已核验，但尚未导入**：

- 文件大小：28,082,489 字节。
- 与官方 `.sha1` 校验文件一致；另记录 SHA-256：`b3fc369b0a1f3ca64537543a403758c4633ed9b0db13c5853268ec018df7d7cd`。
- ZIP 包含 524 个条目，完整性检查通过，没有绝对路径或 `..` 路径条目。
- 包内包含 Grizzly `framework`、`http`、`http-server` 的 `2.3.25` JAR 与 XED 元数据，以及 Tyrus `client`、`core`、`spi`、`container-grizzly-client` 的 `1.13.1` JAR 与 XED 元数据。

该文件位于临时目录，工作区重建后可能消失，不能作为长期备份。

## 必要时使用官方离线包恢复

仅在在线安装持续失败或需要离线安装时执行以下步骤。XIP 用于预填充本地扩展仓库，继续现有安装向导；无需重建数据库或删除数据卷。

1. 下载与运行中 XWiki **完全同版本**的 [17.10.15 官方 XIP](https://nexus.xwiki.org/nexus/content/repositories/releases/org/xwiki/platform/xwiki-platform-distribution-flavor-xip/17.10.15/xwiki-platform-distribution-flavor-xip-17.10.15.xip)，并核对其官方校验文件。已有本地文件可在重新核验后复用。
2. 按当前环境选择正确的 Compose 配置。为避免与安装任务同时写入，先停止 XWiki 应用，保留数据库与命名卷。
3. 将包内容解压到 `<permanentDirectory>/extension/repository`。本镜像对应容器路径为 `/usr/local/xwiki/data/extension/repository`。直接使用 ZIP 内的扩展目录结构，不增加额外顶层目录；**保留已有文件，不覆盖**。
4. 确保运行 XWiki 的用户对新文件有写权限，然后启动 XWiki。官方文档要求运行中的 XWiki 在导入后重启，以读取本地扩展。
5. 打开当前实例的 `http://127.0.0.1:8080/`，继续 Distribution Wizard。向导应使用本地扩展完成安装；验证安装结果后再更新本记录的状态。

官方文档还介绍了用空的 `extension.repositories=` 禁用远程扩展仓库，适用于完全离线环境。本次仅准备 XIP 备用，不执行该配置变更。

参考：[官方离线安装步骤](https://www.xwiki.org/xwiki/bin/view/documentation/xs/admin/installation/install-offline/)；[Maven Resolver 1.9.24 重试默认值](https://github.com/apache/maven-resolver/blob/maven-resolver-1.9.24/maven-resolver-api/src/main/java/org/eclipse/aether/ConfigurationProperties.java)。
