# 第三阶段：Office 编辑接入调研

调研日期：2026-11-12。本文依据官方文档和公开源码核对；没有部署 Office 服务、构建或安装连接器，也没有完成浏览器编辑及保存回写实测。

**当前状态：暂缓执行第三阶段。** 第二阶段尚无企业既有模型端点，不能把模型联调记为完成；同时缺少企业已有 Collabora/CODE 的地址、版本、网络及接入信息。按 POC 阶段顺序先补齐前置条件。这是本项目的执行顺序，Office 编辑本身不依赖大模型。

恢复第三阶段时，优先复用企业已经运行的 Collabora/CODE；只有确认没有可复用服务后，才在 Collabora CODE 与 ONLYOFFICE Docs Community 中选择一套。当前不部署两套，不申请付费试用、不发起采购，也不将临时试用当作长期免费方案。

## 服务选型事实

| 项目 | ONLYOFFICE Docs Community | Collabora CODE |
| --- | --- | --- |
| 开源许可 | AGPLv3，现行发行另有署名、版权、修改标记等附加条款及独立商标政策；应保留发行版本附带的完整许可 | 主要为 MPL 2.0，包含其他第三方开源许可证；不能把整个依赖树概括为单一许可证 |
| 获取与维护 | 官方提供免费自托管版本；无保证的技术支持/SLA，由使用方负责更新与运维 | 官方免费 Development Edition，滚动发布，无 SLA 或长期支持；官方不推荐生产环境，但适合试验及小团队评估 |
| 并发限制 | **从 9.4 起已取消旧的 20 同时连接硬限制**；现行比较表写的是建议最多 20 用户。不能把旧版限制写成现行版本事实 | 官方针对 **26.04.2.4** 说明：默认模式没有文档/连接数上限，但保留欢迎及反馈弹窗；Home Mode 才限制 20 连接、10 文档 |
| 部署形态 | 独立 Document Server，浏览器加载编辑器，连接器提供文件下载与保存回调 | 独立 CODE 服务；连接器实现 WOPI 文件访问、权限及写回，浏览器与服务建立编辑会话 |
| 资源依据 | 当前 Docker 官方要求：单核 2 GHz 或以上、4 GB RAM、40 GB 可用磁盘、至少 4 GB swap；按文档数量、大小实测调整 | 容量随并发及文档复杂度变化。不要把 Nextcloud 内嵌 CODE 的规格直接用作独立 CODE 容量承诺；以所选版本的硬件指南及 POC 测量为准 |
| POC 定位 | 新建独立服务的候选，适合以 `.docx` 为最小验证格式 | **已有服务时优先复用**，避免新增服务和重复运维 |

依据：[ONLYOFFICE 版本比较](https://www.onlyoffice.com/compare-editions)、[9.4 发布说明，2026-05-19](https://www.onlyoffice.com/blog/2026/05/onlyoffice-docs-9-4)、[Community 许可 FAQ](https://helpcenter.onlyoffice.com/docs/installation/community/faq)、[Docker 硬件要求](https://helpcenter.onlyoffice.com/docs/installation/community/docker/sys-reqs)、[Collabora 开源许可说明](https://www.collaboraonline.com/terms/collabora-online-mplv2/)、[CODE 官方介绍](https://www.collaboraonline.com/code/)、[Collabora FAQ](https://www.collaboraonline.com/faqs/)、[26.04.2.4 模式与连接限制的官方论坛答复](https://forum.collaboraonline.com/t/does-collabora-code-26-04-2-4-have-any-user-or-concurrent-connection-limits/5023/2)、[Collabora 容量指南](https://sdk.collaboraonline.com/docs/technotes/hardware_provisioning.html)。

注意：9.4 同时简化了 ONLYOFFICE Community 架构，发布说明称去除了 RabbitMQ 和数据库依赖；旧版安装架构不能直接套用到新版。应锁定实际镜像 tag 与 digest 后，再按对应发行文档配置。资源表仍采用当前官方 Docker 要求，没有根据“架构简化”自行缩减资源。

## XWiki 连接器：商业发行与开源源码分开判断

两个当前连接器都由 **XWiki SAS** 维护，公开源码位于 `xwikisas`；不能因为出现在 XWiki Extensions 目录就称其为免费社区发行。它们不是 XWiki Standard 核心自带的 Office 在线编辑功能。

| 核对项 | ONLYOFFICE 连接器 | Collabora 连接器 |
| --- | --- | --- |
| 仓库 | [xwikisas/application-onlyoffice-connector](https://github.com/xwikisas/application-onlyoffice-connector) | [xwikisas/application-collabora](https://github.com/xwikisas/application-collabora) |
| 已核对稳定 tag | `application-onlyoffice-connector-2.6.5` | `application-collabora-1.8.4` |
| 主分支当日状态 | `master` 为 `2.6.6-SNAPSHOT` | `main` 为 `1.8.5-SNAPSHOT` |
| 源码许可 | LGPL 2.1；源码头允许 2.1 或后续版本 | LGPL 2.1+ |
| 最低 XWiki | 15.10 | 15.10 |
| 稳定 tag 的 Maven parent | `com.xwiki.parent:xwikisas-parent-platform:15.10` | 同左 |
| 稳定 tag 的许可组件 | UI 依赖 `com.xwiki.licensing:application-licensing-licensor-api:1.32.3` | UI 依赖同一组件、同一版本 |
| 服务兼容性证据 | 商店当前说明测试过 Document Server **8.2 至 9.0.4**；并未证明 9.4/10.0 兼容 | 使用 WOPI；本次未找到足以承诺所选 CODE 版本兼容的完整版本矩阵，须实测 |
| 商业发行 | 商店安装流程要求有效许可证，包括可选试用；不是安装即长期免费 | 商店标为 Pro，安装流程同样需要许可证 |

固定版本源码依据：

- ONLYOFFICE：[2.6.5 根 POM](https://github.com/xwikisas/application-onlyoffice-connector/blob/application-onlyoffice-connector-2.6.5/pom.xml)、[2.6.5 UI POM](https://github.com/xwikisas/application-onlyoffice-connector/blob/application-onlyoffice-connector-2.6.5/application-onlyoffice-connector-ui/pom.xml)、[2.6.5 API POM](https://github.com/xwikisas/application-onlyoffice-connector/blob/application-onlyoffice-connector-2.6.5/application-onlyoffice-connector-api/pom.xml)、[许可证](https://github.com/xwikisas/application-onlyoffice-connector/blob/application-onlyoffice-connector-2.6.5/LICENSE)。
- Collabora：[1.8.4 根 POM](https://github.com/xwikisas/application-collabora/blob/application-collabora-1.8.4/pom.xml)、[1.8.4 UI POM](https://github.com/xwikisas/application-collabora/blob/application-collabora-1.8.4/application-collabora-ui/pom.xml)、[1.8.4 Default POM](https://github.com/xwikisas/application-collabora/blob/application-collabora-1.8.4/application-collabora-default/pom.xml)、[许可证](https://github.com/xwikisas/application-collabora/blob/application-collabora-1.8.4/LICENSE)。
- 发行说明：[ONLYOFFICE 商店页面](https://store.xwiki.com/xwiki/bin/view/Extension/OnlyOfficeConnectorApplication)、[Collabora 商店页面](https://store.xwiki.com/xwiki/bin/view/Extension/Collabora%20Connector%20Application%20%28Pro%29/)。

两个仓库均有 2026 年更新；这说明仍有维护活动，不代表任何指定版本组合已经验收。最低 XWiki 版本也不等于承诺兼容全部更高版本。特别是 ONLYOFFICE 商店页面同时保留了旧的“建议 7.0.0”段落与新的“已测试 8.2—9.0.4”说明，不能任选其一作为当前安全基线；应以锁定版本和实际回归测试为准。

### 合法自构建的边界

[XWiki Store FAQ](https://store.xwiki.com/xwiki/bin/view/Store/FAQ)明确说明：商店应用开源，但不全是免费发行；具备技术能力者可以自行构建。[XWiki 维护者的官方论坛答复](https://forum.xwiki.org/t/diagram-application-in-the-xwiki-playground/8311/5)进一步说明：原样编译与商业发行来自相同源码，仍保留许可限制；遵守 LGPL 2.1 的自定义修改和构建是允许的。

因此：

- 不能说“商业连接器开源，所以原样 `mvn package` 后即可免许可运行”。两个稳定 tag 的 UI POM 都明确引入许可组件，且配置了被许可覆盖、公开或豁免的页面。
- 也不能说“所有自行编译均违法”或“必须购买”。合规维护 LGPL fork 是官方认可的技术路线，但需要维护构建、依赖、升级、版权声明及分发义务；它不是已交付的免费安装包。
- 本次没有删除许可依赖、修改许可判断、伪造许可证、修改商业二进制或借用他人密钥。后续若选择自维护开源 fork，应以完整许可证与上述作者许可为依据建立独立构建与维护记录；不能把破解商业发行当作部署步骤。
- 其他产品的“可以申请免费许可证”不能推导为本企业可长期免费使用这两个连接器。免费试用也不满足长期免费目标。

## 构建路径备查：仅为后续验证命令，未执行

构建对象是 **XWiki 连接器**，不是 Office 引擎。Office 引擎优先采用官方发行镜像；不要为了本 POC 无必要地从头构建 LibreOffice/Collabora 或 ONLYOFFICE 全部源码。

构建环境依据：[XWiki 官方构建说明](https://dev.xwiki.org/xwiki/bin/view/Community/Building/)要求按目标分支选 JDK；15.10 对应 Java 11。Maven 使用官方推荐的 3.9.x，并记录精确版本。运行中的 XWiki/JDK 版本与构建基线分别核对。

Maven settings 需要配置官方 XWiki releases/plugin 仓库，以及 XWiki SAS 的 `public-store-releases` 仓库。后者地址来自固定 parent POM：`https://nexus.xwiki.com/nexus/content/repositories/public-store-releases/`。Collabora 根 POM 没有像 ONLYOFFICE 那样重复声明此仓库，解析尚未下载的 parent 时尤其需要在 settings 中声明。不要假设依赖都在 Maven Central，也不要用 `latest` 或 SNAPSHOT 生成 POC 基线。

Parent 源码证据：[xwikisas-parent-15.10](https://github.com/xwikisas/xwikisas-parent/blob/xwikisas-parent-15.10/xwikisas-parent-platform/pom.xml)。该 parent 继续继承 `org.xwiki.contrib:parent-platform:15.10`，并使用 `org.xwiki.contrib:managed-dependencies-maven-plugin:1.0`。

以下路径都是未来验证目录；本次没有创建这些 checkout、settings 或构建产物。`/path/to/poc-maven-settings.xml` 需事先依据上述官方仓库说明准备，不能原样执行占位路径。

```bash
# 二选一。已有 CODE/Collabora 时优先核对这一套。
git clone --branch application-collabora-1.8.4 --depth 1 \
  https://github.com/xwikisas/application-collabora.git \
  /workspace/office-build/application-collabora
cd /workspace/office-build/application-collabora
mvn -s /path/to/poc-maven-settings.xml -B clean verify
mvn -s /path/to/poc-maven-settings.xml -B dependency:tree

# 只有另行选定 ONLYOFFICE 路线时才执行这一组。
git clone --branch application-onlyoffice-connector-2.6.5 --depth 1 \
  https://github.com/xwikisas/application-onlyoffice-connector.git \
  /workspace/office-build/application-onlyoffice-connector
cd /workspace/office-build/application-onlyoffice-connector
mvn -s /path/to/poc-maven-settings.xml -B clean verify
mvn -s /path/to/poc-maven-settings.xml -B dependency:tree
```

这些命令仅描述原样构建，没有关闭许可检查。即便成功产出 XAR/JAR，也不能据此宣告免许可运行或 Office 编辑已通过。

| 连接器 | 需要整体核对的模块与依赖 | 预期产物路径，尚未生成 |
| --- | --- | --- |
| ONLYOFFICE 2.6.5 | `websocket`、`api`、`ui`、`webjar`；XWiki oldcore、REST、Office importer/UI、Netflux；`prime-jwt:2.0.0`；`netflux-websocket-webjar:1.2.1`；许可 API 1.32.3 | `application-onlyoffice-connector-ui/target/application-onlyoffice-connector-ui-2.6.5.xar`，以及各 JAR 模块的 `target/` |
| Collabora 1.8.4 | `api`、`default`、`officeserver`、`ui`、`xip`、`webjar`；XWiki REST/oldcore/configuration、UI 组件；许可 API 1.32.3 | `application-collabora-ui/target/application-collabora-ui-1.8.4.xar`，各 JAR 模块与 `application-collabora-xip/target/` |

本次没有解析完整传递依赖树；表中是 POM 可见依赖，不是 SBOM。后续需归档实际 `dependency:tree`、effective POM、构建日志、源码 commit、许可证及产物摘要。不要只导入 UI XAR 而遗漏 Java/WebJar/许可依赖；也不要为了“让它工作”盲目覆盖 XWiki 自带 JAR。

## 恢复执行后的最小 Word 验证方案

范围限定为 **一名有编辑权限的用户、一页测试页面、一个 `.docx` 附件**。先完成打开、修改、保存、关闭及重新下载/打开；暂不把 `.doc` 转换、多人协作、移动端、ODF 往返转换和生产性能纳入第一条成功标准。

优先路径：已有 Collabora/CODE → 核对该实例的版本、WOPI 地址/允许域、TLS 与网络 → 选择企业已有合法连接器许可或有维护责任的合法开源构建 → XWiki 附件编辑入口 → WOPI 读写原附件。没有既有 Collabora 信息时，不擅自假定其存在或可供本 POC 使用。

若确认没有可复用服务，可选择 ONLYOFFICE Docs Community 作为唯一新增服务。使用新版时，要补做与 XWiki 连接器的兼容性验证：商店目前的测试范围止于 9.0.4，不能为了落在旧测试范围内就自动把旧版设为长期安全版本。若连接器许可/维护路径尚未落实，应保留为待办；独立按公开 API 开发一个最小连接器也是可行的工程候选，但不能标成现成插件或已实现功能。

### 保存回写机制与验收

ONLYOFFICE 的公开 API 明确区分编辑器保存和宿主存储落盘：宿主提供 `document.url`、稳定会话 `document.key`、`callbackUrl` 及 JWT；文档服务回调后，宿主再下载编辑结果，保存为 XWiki 附件版本。状态 `2` 表示最终结果可保存，状态 `6` 是 force-save；状态 `3`、`7` 是保存错误，不能返回假成功。正常关闭后的回调通常约十秒，复杂文档可能更久。只有持久化成功才确认成功；重新打开必须读取新的附件内容，避免旧 key/cache 让人误以为回写成功。[保存流程](https://api.onlyoffice.com/docs/docs-api/get-started/how-it-works/saving-file/)、[回调状态与响应](https://api.onlyoffice.com/docs/docs-api/usage-api/callback-handler/)

Collabora 路线使用 WOPI 而非 ONLYOFFICE `callbackUrl`；应确认 CheckFileInfo/GetFile/PutFile、编辑权限及锁处理的实际行为。连接器采用 WOPI 的源码说明见 [README](https://github.com/xwikisas/application-collabora/blob/application-collabora-1.8.4/README.md)。

后续验收必须留下以下证据，本文当前各项均为**未执行**：

1. 浏览器、XWiki、Office 服务之间的双向 URL/DNS/TLS 访问均有效，WebSocket 反向代理正常。
2. 测试 `.docx` 能打开并显示可识别原文；追加唯一测试文字，保存并关闭。
3. XWiki 中产生正确的附件新版本；重新下载的 `.docx` 含新文字，重新打开也一致。
4. 只有查看权限的用户不能编辑/回写；失效 token、未经授权的回调或跨附件写入不能成功。
5. 中断回写网络时显示明确失败，恢复后可安全重试；不得以编辑器“已保存”提示代替 XWiki 附件核验。
6. 记录 XWiki、连接器、Office 服务的精确版本和镜像 digest，以及回调/WOPI 日志中的关联标识；日志不记录 JWT、会话 cookie 或文件正文。

私有化 POC 使用自己的 Office 地址与密钥。ONLYOFFICE 连接器默认可能指向 XWiki SAS 公共测试服务器，不能向该默认地址发送企业附件。对 XWiki 权限的校验、JWT/WOPI token、受限来源及下载目标校验是接入的一部分，不应通过关闭鉴权、放开匿名附件、禁用 TLS 校验或无限制 CORS 解决连通问题。

## 继续之前缺少的信息

- 第二阶段模型接入：企业既有端点及对应调用方式，由第二阶段处理；不要为推进 Office 自动采购或开通外部模型服务。
- 是否已有 Collabora/CODE；若有，需其版本、内部/浏览器可达地址、TLS、WOPI 接入规则和可供 POC 使用的资源范围。
- 实际 XWiki 版本和运行 JDK，允许安装的连接器/构建方式，以及企业是否已有相应合法许可。
- 一份脱敏 `.docx` 和有编辑/只读权限的测试身份，用于最终回写及权限验收。

当前完成的是官方资料及源码核对。没有 Office 服务或连接器的运行验证，不应将此文档计为第三阶段验收通过。
