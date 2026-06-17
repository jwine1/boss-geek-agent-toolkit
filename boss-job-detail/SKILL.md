---
name: boss-job-detail
description: |
  根据 BOSS 直聘岗位 security_id 获取岗位详情，用于 JD 分析、简历建议和面试准备。

  本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 3），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
---

# BOSS 直聘岗位详情获取

通过 `boss detail <security_id>` 获取岗位详情，保存岗位职责、任职要求、技能要求、福利待遇和公司信息。

## 前提条件

- 已安装并登录 `boss-agent-cli`
- 已生成 `output/jobs.json`
- 已生成 `output/scores.json`
- 目标岗位存在 `security_id`

## 用法

单个岗位详情：

```bash
boss detail <security_id>