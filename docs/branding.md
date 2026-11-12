# LuxPedia 品牌配置与维护

产品显示名称采用 **LuxPedia**，仓库仍为 `h3mxxx/manu-wiki`。品牌变更通过官方 REST、Flamingo 主题、数据库 Skin、Wiki 偏好和面板配置完成；没有修改容器内模板、组件名或许可检查。

## 应用

先完成 XWiki Standard 安装；本方案在 17.10.15 LTS 验证。管理员账号文件为 `.secrets/admin_username`、`.secrets/admin_password`。这些文件只在本地保存，不把密码放入命令行或 Git。

```bash
python3 scripts/apply-branding.py          # 只列出计划变更
python3 scripts/apply-branding.py --apply  # 应用配置，变更前记录旧值
```

默认连接当前环境 `http://127.0.0.1:8080`。可设置 `XWIKI_URL`，非本机地址必须使用 HTTPS；不会自动跟随重定向。先确认目标确实是获准操作的试点实例。

此脚本是明确的 LuxPedia 配置方案：会更新首页内容及下表中的品牌字段，不适合未经核对直接用于已有其他自定义首页/主题的实例。旧对象的无关字段保留；新主题按 Iceberg 配置生成。再次应用会比较页面、字段和附件，本实例重复执行为 `0 change(s)`。

## 配置范围

| 项目 | 位置与设置 |
| --- | --- |
| Logo 与配色 | `FlamingoThemes.LuxPedia`，独立于原 Iceberg；白色字标、蓝色导航栏，替代文字“LuxPedia 企业知识库” |
| 浏览器图标 | `XWiki.LuxPediaSkin` 继承 flamingo；附件 `icons.xwiki.favicon16.png`、`icons.xwiki.favicon.svg`、`icons.xwiki.favicon144.png` |
| 站点偏好 | `XWiki.XWikiPreferences` 的 `colorTheme`、`skin`、`title`、`version`、`rightPanels` |
| Wiki 名称 | `XWiki.XWikiServerXwiki.wikiprettyname=LuxPedia`；内部 Wiki ID 不改 |
| 首页与帮助 | `Main.WebHome`、`LuxPedia.Help.WebHome`、`LuxPedia.About.WebHome` 和本地帮助面板 |
| 上游 Help 入口 | 在 `PanelsCode.ApplicationsPanelConfiguration` 中将 `platform.help` 加入应用栏黑名单 |
| 首次欢迎导览 | `Tour.HomepageTour.WebHome` 的 `TourCode.TourClass.isActive=0`，没有删除教程 |
| 上游资讯入口 | `WhatsNew.Code.NewsUIX` 的 `extensionPointId` 置空；仅取消该菜单的显示，不卸载扩展 |

Skin 资源替换采用官方规则：资源路径 `/` 替换为附件名中的 `.`，例如 `icons/xwiki/favicon.svg` 对应 `icons.xwiki.favicon.svg`。参考[官方 Skin 附件说明](https://www.xwiki.org/xwiki/bin/view/documentation/xs/admin/skins/override-attachment/)。

## 权限与开源声明

私有 Wiki 默认拒绝匿名访问，自建主题/图标也会受此限制。仅三个页面明确允许匿名查看：`FlamingoThemes.LuxPedia`、`XWiki.LuxPediaSkin`、`LuxPedia.About.WebHome`，分别用于登录前的样式、图片和公开组件声明。不要在这三页或其附件中存放内部资料。品牌资源及 LuxPedia 帮助空间的编辑、删除限制管理员。

知识页面、草稿、业务附件的权限未放开；匿名拒绝访问的既有检查通过。首页和普通导航不再显示 XWiki 推广外链。后台组件标识、API、技术文档、历史验收截图和原始 LICENSE/NOTICE 保持准确；关于页面说明底层使用 XWiki，避免把品牌替换误写为原创 Wiki 引擎。

SVG 字标和图标是本项目的简单几何/文字资源；PNG 是该 SVG 的 16 和 144 像素渲染版本，没有复用 XWiki Logo。

## 回退

每次有实际变更时，旧字段值写入 `.runtime/branding/<UTC时间>.json`，目录权限 0700、文件 0600，已被 Git 忽略。**这是手工恢复依据，不是可一键重放的完整回滚包**；新增对象的记录没有保存服务器分配的编号。多次应用时，按时间从新到旧检查记录。

使用管理员在相应页面的对象编辑器恢复记录中的原值。恢复本次 v0.1.0 外观的关键设置为：

1. 全局偏好：`colorTheme=FlamingoThemes.Iceberg`、`skin=XWiki.DefaultSkin`、`title=$tdoc.getRenderedTitle('plain/1.0') - XWiki`、`version` 为空；`rightPanels=Help.TipsPanel.WebHome,Panels.MyRecentModifications,Help.SupportPanel.WebHome`。
2. Wiki 显示名称恢复为原值 `Home`；Tour 的 `isActive` 恢复为 `1`；News UIX 的扩展点按快照恢复为 `org.xwiki.plaftorm.drawer`。
3. 在应用栏配置中取消 `platform.help` 的黑名单条目；只操作本次增加的条目。
4. 如需恢复首页，使用 `Main.WebHome` 的 History 选择品牌变更前版本，执行 Rollback 并确认；不要删除后续知识内容。
5. 原主题和原 Skin 一直保留；新建品牌页面可以留存。停用品牌时可撤销这三个页面的匿名查看规则，再核对登录、知识权限和附件。

如果目标实例在应用前已有其他定制，应使用其自己的快照，不能照抄上面的 POC 原值。现有数据仍需按部署文档定期备份；品牌快照不能替代数据库与附件备份。
