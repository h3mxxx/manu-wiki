# POC 使用说明

实际通过与待验收项以 `reports/acceptance.md` 为准，以下是使用路径，不把操作说明当成已验证结果。

## 访问与账号

实例位于当前隔离环境的 `http://127.0.0.1:8080/`，不等于用户电脑的 localhost，也不是公网地址。长期访问需迁移到非生产企业服务器或使用平台提供的环境访问方式。不要为了方便直接暴露数据库或关闭权限。

管理员用户名保存在本地 `.secrets/admin_username`，密码在 `.secrets/admin_password`；不要提交或分享这些文件。试点还提供 `poceditor`、`pocreviewer`、`pocreader` 三个合成测试账号，各自密码在 `.secrets/<用户名>_password`。正式邀请试点成员时应在 Administration → Users 中创建个人账号，避免多人共用管理员。

| 角色 | 目标权限 |
| --- | --- |
| 管理员 | 用户、权限、扩展及整个实例配置 |
| 编辑者 POCEditors | 阅读 Knowledge，在 Drafts 中编写和修改 |
| 审核者 POCReviewers | 阅读/审核草稿，维护 Knowledge 已发布内容 |
| 阅读者 POCReaders | 阅读 Knowledge 和附件，不读草稿、不编辑 |
| 未登录用户 | 不读知识页面或附件；不开放自助注册 |

权限在 wiki 和空间的 Administration → Rights 中管理。页面标题、标签、“Draft”状态都不能代替实际 VIEW 权限。新增子空间继承情况要用阅读者及匿名用户再测一次。

## 知识结构与编辑

- `Knowledge`：已发布示例，含 Technical、Operations 和 Attachments。
- `Drafts`：草稿与审核区域，包含一篇带独立测试标记的合成草稿。
- `Templates.Technical`：技术知识模板。可复制该页面到 Drafts，然后修改标题、负责人、适用版本、步骤、验证与来源。系统的 Templates 根空间也包含官方模板配置，不要整空间删除。

打开页面 → Edit。CKEditor 可编辑标题、正文、列表、表格、链接和图片；等待协作编辑工具栏就绪，点击 `Done` 完成保存，再以阅读者打开检查；本版本的旧 `Save & View` 控件可能被协作工具栏替代。需要源代码时选择 Wiki 编辑模式，页面语法为 XWiki 2.1。不要把 Markdown 代码原样当作 XWiki 语法。

分类可通过嵌套页面和 Tags 实现；少量示例使用技术文档、操作手册两类，不复制 BWIpedia 全量内容。中文页面内容可直接编写，界面语言在用户配置或 Localization 中选择。

## 附件与版本

`Knowledge.Attachments` 包含合成图片、PDF、Word、视频。附件页签支持上传和下载；图片可插入正文。PDF/视频能否内联显示由浏览器及宏配置决定，下载成功不等同于预览成功。

官方镜像内含 LibreOffice，可供 Office 宏转换/预览使用；这不包含浏览器编辑并保存回 Word 的能力。Collabora/ONLYOFFICE 编辑需要第三阶段连接器和引擎，当前未部署。

修改页面后查看底部 History，选择两个版本比较；需要恢复时使用对应版本的 rollback/恢复入口，并确认当前内容和版本号。先在合成页操作，不在真实知识上做恢复演练。重复上传同名附件可产生附件版本，是否保存作者和历史必须另测。

## 搜索与发布

顶部搜索使用 XWiki Solr。可尝试 `MANU-WIKI-PUBLISHED-20261112`、`MANU-WIKI-PDF-20261112`、`MANU-WIKI-DOCX-20261112`。附件解析是异步的，不能用刚上传后的瞬时空结果推断文件不受支持。

Publication Workflow 的配置与角色流程见 `workflow.md`；若尚未安装或验收，则采用人工方式：编辑者在 Drafts 写作，审核者检查，审核通过后由审核者复制到 Knowledge，并在页面注明审核人/日期。此方式只是过渡流程，不冒充扩展自动流转。已发布版本更新也经过草稿审核，阅读者始终只访问 Knowledge。

AI 语义检索、摘要、相关页面推荐与带来源问答仍待已有模型服务接入；当前关键词搜索不能称为语义搜索。配置映射和安全验收见 `ai.md`。
