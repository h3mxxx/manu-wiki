首次核心 Wiki POC 预发布：已在隔离环境实际运行 XWiki Standard 17.10.15 LTS、PostgreSQL 16.15 和 Publication Workflow 2.4.9。

包含 Docker Compose 持久化部署、密钥初始化、可选云代理/CA 配置、一致性备份脚本、合成知识与附件、使用维护说明、版本及许可证清单。

验证结果：8 项接口检查和 13 组浏览器场景通过，包括角色权限、CKEditor 保存、原生历史恢复、附件预览及下载、Solr 页面/PDF/Word 搜索、草稿提交审核和正式发布。容器重建后数据保留，备份校验与读取通过。详见 [基础版本运行测试](https://github.com/h3mxxx/manu-wiki/blob/v0.1.0/reports/baseline-test-2026-11-12.md)。

使用前请阅读 [部署说明](https://github.com/h3mxxx/manu-wiki/blob/v0.1.0/docs/deployment.md)：新实例需要官方安装向导及账号/权限配置；当前云实例仅监听环境内 `127.0.0.1:8080`，此 Release 不提供公共 Wiki 服务。

已知限制：

- 暂无模型端点，AI 扩展、语义检索和问答未部署/验收。
- Office 仅有附件转换预览，未部署在线编辑或保存回写。
- SMTP 未配置，审核通知邮件不可用；页面内审核发布通过。
- Solr 分面可能泄露私有文档存在性，流程并非强制四眼审核；工作流缓存修改警告已记录。
- 完整独立备份恢复、生产并发及安全审计尚未执行。

详见 [全部问题与后续计划](https://github.com/h3mxxx/manu-wiki/blob/v0.1.0/reports/status.md) 和 [变更记录](https://github.com/h3mxxx/manu-wiki/blob/v0.1.0/CHANGELOG.md)。源码归档不含密钥、实例数据库、备份或云运行配置；本版本不自动部署到任何生产环境。
