---
name: boss-job-detail
description: |
  根据 BOSS 直聘岗位 security_id 获取岗位详情，用于 JD 分析、简历建议和面试准备。

  本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 3），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
---

# BOSS 直聘岗位详情获取

通过 `boss detail <security_id>` 获取岗位详情，由 Agent 解析 CLI 输出并保存岗位职责、任职要求、技能要求、福利待遇和公司信息。

## Windows 编码兼容规则

在 Windows + Claude Code 环境中，岗位详情可能包含 GBK 无法编码的 Unicode 字符。Agent 获取详情时应优先使用 PowerShell UTF-8 包装命令：

```powershell
powershell -NoProfile -Command "$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; & 'E:/boss-geek-agent-toolkit/.venv/Scripts/boss.exe' detail '<security_id>'"

本 Skill 不依赖独立详情抓取脚本。岗位详情由 Agent 根据本文件规则直接调用 CLI 获取。

## 前提条件

- 已安装并登录 `boss-agent-cli`
- 已生成 `output/jobs.json`
- 已生成 `output/scores.json`
- 目标岗位存在 `security_id`
- Agent 具备执行命令、读取文件和写入文件的能力

## 输入文件

| 文件 | 用途 |
|---|---|
| `output/jobs.json` | 最新一次岗位搜索结果 |
| `output/scores.json` | 最新一次岗位评分结果 |

## 输出目录

```text
output/details/