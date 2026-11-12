# 实例验收记录

日期：2026-11-12（Asia/Shanghai）。服务器日志时间为 UTC。以下均针对本次合成 POC 数据，不能推导为生产环境或所有格式验收通过。

发布前追加运行回归与实际日志问题见[基础版本运行测试](baseline-test-2026-11-12.md)。

## 环境与安装

- Debian13.6；5 CPU、约17 GiB内存、初始约30 GiB可用磁盘。
- Docker29.9.2 / Compose2.40.3；开始时无容器，无可复用数据库/模型/Office服务。只检查了当前云环境，不代表已检查企业内网。
- XWiki17.10.15 LTS 官方 postgres-tomcat 镜像；PostgreSQL16.15-bookworm。
- 实际容器内：Temurin21.0.13+9-LTS、Tomcat10.1.61、Solr9.4.1；CKEditor运行时报告4.22.1。
- Standard Flavor 17.10.15 通过官方向导安装，Publication Workflow2.4.9通过官方 Extension Manager 安装。
- DB与XWiki永久目录分别持久化在独立命名卷；数据库未映射宿主端口，Wiki只映射127.0.0.1:8080。
- 凭据在 `.secrets/`，Git忽略，未写入报告；没有调用外部模型，没有采购或商业试用。

## 已执行的核心验收

| 项目 | 实际结果与证据 |
| --- | --- |
| 初始化重跑 | 连续运行init.sh，数据库密码摘要一致；.env和密码0600、密钥目录0700 |
| Compose | 基础配置与当前云override可解析；云Java代理/CA启用且保留TLS验证 |
| 安装向导 | Admin、Flavor、Orphans、Extensions步骤完成，报告显示安装结束，首页正常 |
| 知识空间 | Knowledge含技术、操作、附件、工作流发布示例；Drafts独立；无BWIpedia迁移 |
| 分类与模板 | 技术/操作标签可见；技术知识模板提供器已创建，Drafts创建界面实际显示“技术知识文档” |
| 账号与权限 | 管理员、poceditor、pocreviewer、pocreader；阅读者可读发布页，读草稿403/REST401，编辑已发布页403 |
| 匿名用户 | 页面及附件REST拒绝访问；初始默认开放行为已配置关闭，随后测试通过 |
| CKEditor | 等待协作工具栏就绪，浏览器修改EditorDemo，点击Done；新正文含MANU-EDITOR-V2，版本1.1→2.1 |
| 原生历史恢复 | History中Rollback至1.1；正文恢复MANU-EDITOR-V1，当前版本3.1，2.1保留在历史 |
| 图片 | architecture.svg在正文加载成功，浏览器naturalWidth>0 |
| PDF | sample.pdf HTTP200/application/pdf、inline；Chromium原生PDF查看器打开，截图pdf.png |
| 视频 | sample.mp4实际播放；duration=2秒，320×180，paused=false |
| Word | sample.docx经内置Office宏/LibreOffice转换，页面显示文档内合成正文；不代表在线编辑回写 |
| 附件完整性 | 四类附件下载SHA256与上传源字节一致 |
| 关键词搜索 | Solr显示技术页面命中；按PDF和DOCX各自唯一标记搜索，均出现Attachment content |
| 搜索权限 | 阅读者搜索草稿唯一短语无结果、无草稿链接或正文；侧栏分面仍有汇总计数，列入一般问题 |
| 发布流程 | 编辑账号启动Drafts.WorkflowDemo并提交，进入validating；审核账号Publish确认后产生Knowledge.WorkflowDemo，作者pocreviewer，目标版本1.1 |
| 发布阅读隔离 | 阅读者可见正式页及标记，直接访问工作流草稿403 |

浏览器证据在 `reports/screenshots/`。测试均使用环境内Chromium，未使用模拟页面。共享Desktop工具返回Browser runtime unavailable，未声称用户电脑可直接访问该地址。

## 持久化与备份

- 已执行 `COMPOSE_FILE=compose.yaml:compose.cloud.yaml ./scripts/backup.sh`，备份目录为本地未跟踪的 `backups/20261112T123913Z.tjdhRK/`，约66 MiB。该归档包含敏感配置，不随代码交付或公开上传。
- 停止XWiki后生成PostgreSQL自定义格式备份及XWiki永久目录归档，随后脚本自动恢复应用。
- `sha256sum -c SHA256SUMS` 五项全部OK；两个tar归档可完整列出；`pg_restore --list` 成功读取257行目录。
- 备份目录0700，数据库/数据/配置归档0600。
- 实际执行双配置 `docker compose up -d --force-recreate db xwiki`，没有删除卷。新容器均healthy。
- 重建后 `python3 tests/smoke.py` **8项全部通过**，验证发布正文、四类附件字节、普通草稿与工作流草稿权限、发布作者、历史列表、回退后的3.1内容均保留。
- 这些结果证明容器重建持久化和备份可读，不等于已经在独立实例恢复数据库/附件；完整恢复演练仍待执行。
- 独立审阅完成：未发现阻塞当前POC的问题。基础/云Compose解析、Shell语法、敏感路径Git忽略均通过。

## 未执行或仅完成研究

- AI LLM/Index1.0.0：完成版本、依赖、许可证、API和权限源码核对；用户暂无模型端点，因此未安装AI扩展、未建语义索引、未执行问答/摘要/推荐/AI ACL验收。普通Solr成功不能替代AI验收。
- Office在线编辑：未部署Collabora/ONLYOFFICE引擎、未构建或安装连接器；未执行Word回写、身份和附件新版本检查。
- Workflow高级项：SMTP未配置，提交审核时邮件连接失败，通知未通过验收；多人并发、拒绝路径、递归子页/删除同步、附件发布同步、强制职责分离未验收。
- 恢复演练：有操作说明；若报告未追加实际独立恢复证据，则完整恢复演练仍未完成。
- 复杂Office排版、扫描PDF/OCR、加密文件、超大附件、正式并发和安全审计不在本轮通过范围。
