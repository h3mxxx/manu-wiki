# 版本发布流程

本仓库使用 SemVer 格式的 `vMAJOR.MINOR.PATCH` 标签。当前为 POC，GitHub Release 标记为预发布；是否转为正式发布由实际验收范围决定。

## 验证与准备

1. 在非生产实例完成当前版本相关运行测试；按阻塞、一般问题、优化项记录结果。未部署或未测试的功能不得写成通过。
2. 检查 Shell/Python 语法、Compose 配置、Git 差异及密钥忽略规则；运行实例已有合成数据的 `python3 tests/smoke.py`，需要时补充浏览器验收。
3. 更新 `CHANGELOG.md`、验收报告和已知问题，提交所有发布文件，确认工作区干净。只发布 Git 跟踪的源文件，不打包整个工作目录。
4. 后续版本通过工作分支和 PR 审查并合入 `main`；受保护分支或必需检查未通过时不绕过。首次发布时远端完全为空，没有可比较的 PR 基线，因此直接初始化 `main`。

## 标签与 Release

以下以首次 `v0.1.0` 为例，在验收提交上执行，禁止覆盖已有标签或强制推送：

```bash
git push origin HEAD:refs/heads/main
git tag -a v0.1.0 -m "manu-wiki v0.1.0: core Wiki POC prerelease"
git push origin refs/tags/v0.1.0
gh release create v0.1.0 \
  --repo h3mxxx/manu-wiki \
  --verify-tag --prerelease --latest=false \
  --title "v0.1.0 — 核心 Wiki POC" \
  --notes-file reports/release-v0.1.0.md
```

GitHub 自动提供标签源码 ZIP / tar.gz。本次不额外上传镜像、第三方扩展包、实例数据或备份；组件各自许可证见 `components.md`。后续如需自定义制品，再增加制品校验和与构建记录。

## 发布后确认

- 回读远端 `main` 和解析后的标签提交，确认两者均等于验收提交。
- 回读 Release，确认 `tagName`、标题、说明、源码包链接正确，`isDraft=false`、`isPrerelease=true`。
- 发布代码与部署升级分开处理；创建 Release 不自动更新任何生产服务器。
- 标签一旦对外发布保持不变。修复通过新版本发布；运行实例回退需按备份恢复说明操作，不假定降级镜像能安全回退数据库。
