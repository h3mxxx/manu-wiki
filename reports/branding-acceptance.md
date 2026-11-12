# LuxPedia 品牌验收

日期：2026-11-12。对象为当前隔离 POC，XWiki 17.10.15 LTS。

已替换页头字标、SVG/PNG favicon、首页、浏览器标题、Wiki 显示名称和页脚；新增站内帮助及关于/组件声明。普通首页、侧栏和抽屉中的上游推广入口已移除，默认 XWiki 欢迎导览关闭。上游组件、许可证、技术文档和旧版本记录仍保留真实名称。

## 实际验证

- 匿名登录页 Logo 加载成功，标题为“登录 - LuxPedia”；三类 favicon 资源返回 HTTP 200 / image 类型。
- 关于页允许匿名查看；知识页仍拒绝匿名读取。公开范围仅为两个品牌资源页和关于页。
- 阅读者首页标题为“LuxPedia - 企业知识库”，Logo 替代文字正确，无 XWiki 文案、无外部链接、无首次导览遮罩。
- 抽屉不再出现上游资讯项；站内帮助和关于页可达，关于页保留 XWiki 组件声明；阅读者编辑帮助页返回 403。
- 390 像素窄屏页面无横向溢出；桌面及窄屏截图已保存。
- 管理员外观配置页可达；CKEditor 仍可加载。本轮未为了品牌检查再次修改历史演示页。
- `python3 tests/smoke.py`：8 项全部通过，覆盖匿名拒绝、草稿隔离、附件、历史和已发布工作流结果。
- 重复执行 `python3 scripts/apply-branding.py --apply`：`0 change(s)`，未追加对象/页面版本。
- 独立脚本审查、Python 语法和 Git 差异检查通过。

## 已处理问题与边界

首次应用时登录页品牌附件返回 401，原因是自建主题/Skin 继承私有 Wiki 的匿名访问限制；仅对指定品牌页添加查看权限后复验通过。没有放开 Knowledge、Drafts 或业务附件。

Skin 的 REST 标题由皮肤名称返回；脚本统一使用 LuxPedia，修复了重复应用时无意义的标题更新。

品牌快照用于手工恢复，不是完整自动回滚包。官方后台及通用控件仍可能显示 XWiki 技术名称或英文；本轮不是完整界面本地化，也没有替换文章中真实描述上游组件的名称。

截图：[首页](screenshots/luxpedia-home.png)、[登录页](screenshots/luxpedia-login.png)、[窄屏](screenshots/luxpedia-mobile.png)。配置与回退见 [品牌维护说明](../docs/branding.md)。
