
## 2. `job-matcher/SKILL.md`

```markdown
---
name: job-matcher
description: |
  根据求职画像和岗位搜索结果进行初筛评分，输出岗位推荐等级、推荐理由和风险提示。

  本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 2），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
---

# 岗位匹配评分

读取 `geek-profile/profile.yaml` 和 `output/jobs.json`，对岗位进行规则化评分，生成 `output/scores.json`。

## 前提条件

- 已生成 `output/jobs.json`
- 已配置 `geek-profile/profile.yaml`
- 已存在 `job-matcher/scripts/score_jobs.py`

## 用法

```bash
python job-matcher/scripts/score_jobs.py