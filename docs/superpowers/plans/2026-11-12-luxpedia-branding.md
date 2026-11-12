# LuxPedia Branding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 将隔离 Wiki 的用户入口品牌替换为 LuxPedia。

**Architecture:** 使用独立 Flamingo 主题、站点偏好和可维护的面板配置。通过官方 REST 接口应用，保留旧配置快照和原主题。

**Tech Stack:** XWiki 17.10.15、Flamingo、Python 标准库、SVG、Chromium。

**Spec:** `docs/superpowers/specs/2026-11-12-luxpedia-branding-design.md`

## Global Constraints

- 用户名称选择：LuxPedia；仅当前隔离 POC。
- 不删除知识、不改核心文件、不覆盖已有发布标签。
- 普通界面清理推广链接；保留组件技术名称和开源声明。

## Review Focus

- 匿名登录页能加载 Logo/图标，同时知识权限保持关闭。
- 新用户首次访问不再弹出上游品牌欢迎导览。
- 管理员仍能进入管理、编辑和扩展配置。
- 配置重复应用不追加重复对象，恢复方式清楚。
- 窄屏字标与导航不重叠，站内帮助与关于链接可达。

## Task 1: 配置与品牌资源

- [x] 在 `branding/` 保存字标、图标、首页及帮助/关于内容。
- [x] 在 `scripts/apply-branding.py` 实现限定范围、备份优先的配置应用，记录到 `docs/branding.md`。
- [x] 应用到隔离实例，验证 Logo、标题、导航、页脚和登录前后显示。

## Task 2: 验证与交付

- [x] 检查窄屏、匿名权限、管理入口及重复应用结果；执行 `python3 tests/smoke.py`。
- [x] 保存截图及验收记录，更新 README、变更记录，独立审阅后按版本流程交付。
