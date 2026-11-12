# Publication Workflow 现成扩展核对与 POC 操作说明

核对日期：2026-11-12。目标环境：XWiki 17.10.15 LTS。

**状态：2.4.9已安装到XWiki17.10.15；两角色的起草→提交审核→审核者发布流程已在实例实测通过。完整三角色、通知、目录树和附件同步等仍待验收，详见文末。**

## 选用扩展

| 项目 | 核对结果 |
| --- | --- |
| 名称 | Publication Workflow Application |
| 当前稳定版 | `2.4.9`；官方 Maven 元数据的 `latest` 和 `release` 均为该值 |
| 安装 Extension ID | `org.xwiki.contrib.workflow-publication:xwiki-workflow-publication-application` |
| 类型 | XAR，支持 Extension Manager |
| 直接依赖 | `org.xwiki.contrib.workflow-publication:xwiki-workflow-publication-api:2.4.9` |
| 最低支持版本 | 发布 tag 的 README 明确为 **XWiki 12.10.4**，发布 POM 采用相同平台基线 |
| 本 POC 兼容性 | 已安装到17.10.15并验证最小流程；不代表全部功能兼容性认证 |
| 许可 | 扩展目录标为 **LGPL 2.1**；发布 JAR 的 `META-INF/LICENSE` 为 2.1，源码文件头允许 2.1 或后续版本。README 写作 LGPL v3，与其他材料不一致，应保留此差异，不能把 README 单行当作唯一依据 |

官方依据：[扩展目录](https://extensions.xwiki.org/xwiki/bin/view/Extension/XWiki%20Publication%20Workflow%20Application)、[2.4.9 扩展元数据](https://extensions.xwiki.org/xwiki/rest/repository/extensions/org.xwiki.contrib.workflow-publication%3Axwiki-workflow-publication-application/versions/2.4.9)、[Maven 版本元数据](https://nexus.xwiki.org/nexus/content/groups/public/org/xwiki/contrib/workflow-publication/xwiki-workflow-publication-application/maven-metadata.xml)、[发布 tag README](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/README.md)、[发布 POM](https://nexus.xwiki.org/nexus/content/groups/public/org/xwiki/contrib/workflow-publication/xwiki-workflow-publication/2.4.9/xwiki-workflow-publication-2.4.9.pom)、[含 LICENSE 的发布 API JAR](https://nexus.xwiki.org/nexus/content/groups/public/org/xwiki/contrib/workflow-publication/xwiki-workflow-publication-api/2.4.9/xwiki-workflow-publication-api-2.4.9.jar)。

## 用现成界面配置

以下是完整三角色配置参考；当前实例采用更简单的两角色配置，实际名称见文末，无需编写工作流代码。

1. 管理员在扩展管理器中按上述 ID 安装 `2.4.9`，核对应用及依赖的安装结果。
2. 在 Wiki 管理界面创建三个组：`XWiki.ManuContributors`（作者）、`XWiki.ManuModerators`（审核）、`XWiki.ManuPublishers`（批准发布）。用三个普通测试账号分别加入，另设普通读者账号。
3. 在 `PublicationWorkflow` 下使用 `PublicationWorkflowConfigTemplate` 模板建立配置页，例如 `PublicationWorkflow.ManuWorkflow`。将三组分别填入 contributor、moderator、validator；界面中的 Publishers 对应源码字段 `validator`。
4. 建立独立草稿区域与发布区域，例如 `ManuDrafts`、`ManuPublished`。将 `PublicationWorkflow.PublicationWorkflowPanel` 加入两区域的面板配置。内置 `{{publicationworkflow /}}` 宏也可提供操作界面；优先使用面板。
5. 在草稿区域新建一篇测试页，选择配置页和发布目标后启动流程。首轮只测单页，暂不选 `includeChildren`。依次用作者提交审核、审核员提交审批、发布员批准并确认发布；另测拒绝返回和再次编辑。

官方用法见[扩展使用说明](https://extensions.xwiki.org/xwiki/bin/view/Extension/XWiki%20Publication%20Workflow%20Application#HUsage)。配置字段及默认值见[2.4.9 配置类](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-application/src/main/resources/PublicationWorkflow/PublicationWorkflowConfigClass.xml)。

建议首轮保持 `Set drafts to hidden = Yes`、`Skip draft rights = No`、`Move strategy = Do nothing`，默认目标设为发布区域。`hidden` 只是隐藏页面的展示标记，草稿保密须靠查看权限。可选 viewer/commenter 组先留空；需要额外旁观或评论角色时再单独验收。

若只需要一次审核，可不设置 moderator，由 publisher 承担审核与发布。三组方案则便于演示作者、审核、批准发布三个职责，但扩展没有强制同一人不得兼任。

## 状态、角色与权限

完整三组配置的主流程为：

```text
draft → moderating → validating → valid → published
           │              │
           └→ draft       └→ moderating

published → Edit draft → draft（旧发布页保留）
```

`valid` 是已批准但尚未发布的可选中间状态；界面的批准和发布动作可连贯完成。以下是 `skipDraftRights=false` 时扩展对**草稿页**设置的权限，不是发布页权限：

| 草稿状态 | 作者组 | 审核组 | 批准发布组 |
| --- | --- | --- | --- |
| `draft` | 查看、评论、编辑 | 查看、评论、编辑 | 查看、评论、编辑 |
| `moderating` | 查看 | 查看、评论、编辑 | 查看、评论、编辑 |
| `validating` / `valid` | 查看 | 查看 | 查看、评论、编辑 |
| `published` | 保留发布前 ACL | 保留发布前 ACL | 保留发布前 ACL |

重新进入草稿状态会恢复三组编辑权限。Publisher 可执行审核与贡献操作，Moderator 可执行贡献操作，Wiki 管理员可执行所有这些操作。因此验收必须使用分离的普通账号，不能只用管理员看到按钮便断言权限正确。

源码依据：[草稿权限](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L590)、[审核权限](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L740)、[审批权限](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L833)、[角色能力检查](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationRoles.java#L135)。

**发布区域的 ACL 由管理员另行设置。** 应让普通读者可读发布页、不能读草稿，业务账号通过工作流修改内容，并验证其无法绕过流程直接编辑发布页。不要把草稿自动权限或页面 hidden 标记当作发布区域的权限配置。

## 草稿与发布副本的行为

一份内容有草稿和发布目标两个页面引用。首次发布创建目标；再次修改草稿不会改变已经发布的内容，再次发布才更新目标。开始新一轮贡献不会自动撤下旧发布版。

发布同步正文、元数据、常规对象、附件及语言版本，保存为目标页的新修订，不搬运整个草稿修订历史。草稿的评论、评分、ACL 和工作流对象不直接覆盖目标对应对象；目标自己的权限得以保留。精确过滤类包括 `XWiki.XWikiComments`、`XWiki.RatingsClass`、`XWiki.AverageRatingsClass`、`XWiki.XWikiRights`、`XWiki.XWikiGlobalRights`、`PublicationWorkflow.PublicationWorkflowClass`。

发布不是只新增内容的备份：草稿删除的附件或翻译可在下次发布时从目标同步移除。勾选 `includeChildren` 才把子页面纳入流程及递归发布，同时会同步删除没有草稿对应项的已发布子页。首轮单页验收后再单独测试目录树。

源码依据：[发布操作](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L954)、[重新编辑](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L1083)、[复制过滤及附件同步](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L1263)、[目标、翻译与子页处理](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/xwiki-workflow-publication-api/src/main/java/org/xwiki/workflowpublication/internal/DefaultPublicationWorkflow.java#L1465)。

归档会将发布内容标为 hidden；取消发布会删除发布目标并把内容送回草稿。两项应使用可丢弃的测试内容另行验证。[官方行为说明](https://extensions.xwiki.org/xwiki/bin/view/Extension/XWiki%20Publication%20Workflow%20Application#HUsage)

## 当前实例验收记录

实际执行日期：2026-11-12。配置页 `PublicationWorkflow.POC`：contributor=`XWiki.POCEditors`，moderator为空，validator=`XWiki.POCReviewers`，`draftsHidden=1`，`skipDraftRights=0`。因此作者提交后直接进入validating，由审核者批准发布。草稿 `Drafts.WorkflowDemo.WebHome`，发布目标 `Knowledge.WorkflowDemo.WebHome`，不包含子页。

| 验收项 | 预期 | 当前结果 |
| --- | --- | --- |
| 安装 | 应用及依赖在 17.10.15 成功安装，版本为 2.4.9 | 已通过官方扩展管理器安装 |
| 作者起草 | 作者能建草稿、提交审核；无发布权限 | poceditor启动流程并提交，进入validating；作者界面无发布操作，未完整测试伪造请求 |
| 审核 | 审核员能编辑审核稿、退回作者或提交审批 | 本轮审核和批准发布合并为POCReviewers；拒绝/独立moderator未测 |
| 批准发布 | 发布员能批准、拒绝并发布到指定目标 | pocreviewer点击Publish并确认，产生目标1.1，记录作者pocreviewer；拒绝路径未测 |
| 读者隔离 | 普通读者看到发布版，无法查看草稿 | pocreader可见发布标记，直接读工作流草稿HTTP403 |
| 防绕过流程 | 各普通业务账号不能直接编辑发布目标 | 阅读者编辑403；审核组仍有Knowledge编辑权，未实现强制四眼审核 |
| 旧版保留 | 新草稿审核期间，读者仍看到旧发布版 | 未实际验收 |
| 附件及历史 | 发布后附件可用；目标新增修订，草稿历史仍在草稿页 | 未实际验收 |
| ACL 保留 | 再次发布不覆盖发布区权限 | 未实际验收 |
| 通知 | SMTP 配好后，审核、审批和拒绝等邮件到达预期收件人 | 未实际验收 |
| 可选目录树 | includeChildren 的复制、删除与权限继承符合预期 | 未实际验收 |

邮件到达依赖 SMTP 和测试用户邮箱，不能以界面提交成功代替送达结果。上游还提供了[人工测试场景](https://github.com/xwiki-contrib/workflow-publication/blob/xwiki-workflow-publication-2.4.9/tests.md)，可作为后续回归清单参考。
