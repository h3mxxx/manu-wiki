# 组件、版本、许可证和费用

核对日期：2026-11-12。软件费用与实际模型调用/服务器费用分开；本次没有采购、订阅或付费试用。准确运行状态见 `reports/acceptance.md`。

| 组件 | 固定/核对版本 | 许可与费用 | 状态 |
| --- | --- | --- | --- |
| XWiki Standard | 17.10.15 LTS | LGPL 2.1+，免费开源；默认页面内容另遵循其CC-BY许可 | 已启动，核心验收见报告 |
| PostgreSQL | 16.15，bookworm镜像 | PostgreSQL License，免费 | 已启动、独立命名卷 |
| Tomcat（镜像内） | 10.1.61 | Apache-2.0，免费 | 容器日志核实 |
| Java（镜像内） | Temurin21.0.13+9-LTS | OpenJDK GPLv2 + Classpath Exception | 使用官方镜像自带运行时 |
| 内嵌 Solr | 9.4.1（实际JAR） | Apache-2.0，免费 | 无宿主端口映射 |
| CKEditor | XWiki集成17.10.15；运行时报告4.22.1 | 编辑器可选GPL2+ / LGPL2.1+ / MPL1.1+；集成按XWiki许可，未购买CKEditor服务 | 浏览器编辑/保存/回退已验证 |
| LibreOffice（镜像内） | 26.2.7（Dockerfile声明） | MPL2.0/LGPLv3+及第三方许可，免费 | 用于转换/预览，不等于在线编辑服务 |
| LLM Application / Index | 1.0.0 | LGPL2.1+，免费 | 安装与实测状态见报告 |
| Publication Workflow | 2.4.9 | 发布POM/源码头LGPL2.1+；README写LGPLv3，差异见workflow.md | 安装与实测状态见报告 |
| 模型服务 | 未提供端点/模型ID | 既有服务可能另有API费用和模型许可 | 未调用、未部署 |
| ONLYOFFICE Docs Community | 候选，未锁定运行版本 | AGPLv3及附加条款；免费社区发行 | 未部署 |
| Collabora CODE | 候选，调研26.04.2.4限制说明 | 主要MPL2.0及第三方许可；免费开发版 | 未部署 |
| XWiki Office连接器 | ONLYOFFICE2.6.5 / Collabora1.8.4 | 源码LGPL2.1+，商业发行有许可组件；自构建边界见office.md | 未构建、未部署 |
| Docker Engine / Compose | 29.9.2 / 2.40.3 | Apache-2.0为主，已有环境，不新增Docker Desktop订阅 | 复用 |
| 宿主 Debian | 13.6 | 各软件包许可证 | 当前隔离云环境 |

## 已拉取镜像的内容摘要

```text
xwiki:17.10.15-postgres-tomcat
  xwiki@sha256:3dd6f6642f98ff31c330d513e9801aafafc22c9b5573e68951bf82d839d7256e
postgres:16.15-bookworm
  postgres@sha256:5264710be20f409750ac6dc4e5706dcef929c87e241605463f0f9aefa932a8d9
```

这是本次拉取的manifest digest记录；Compose固定版本tag，若要求字节级固定，可将 `.env` 镜像值改为 `仓库:tag@sha256:摘要`。升级前备份、在独立环境复核并更新记录，不盲目使用latest。

来源：[XWiki发布](https://www.xwiki.org/xwiki/bin/view/Download/)、[XWiki许可证](https://www.xwiki.org/xwiki/bin/view/Main/License)、[官方镜像清单](https://github.com/docker-library/official-images/blob/master/library/xwiki)、[本次Dockerfile](https://github.com/xwiki/xwiki-docker/blob/35bc01b3e196afafcee350f903f95e0908f04643/17/postgres-tomcat/Dockerfile)、[PostgreSQL许可证](https://www.postgresql.org/about/licence/)。AI/Workflow/Office的固定源码证据分别见对应专题文档。此表不是完整传递依赖SBOM；后续对外分发时需保留镜像及扩展自带许可证/NOTICE并另做完整依赖审计。

CKEditor许可来源：[4.22.1 LICENSE](https://github.com/ckeditor/ckeditor4/blob/4.22.1/LICENSE.md)。4.23+商业LTS条款不应套用到本实例报告的4.22.1；后续应随官方XWiki补丁维护编辑器集成。
