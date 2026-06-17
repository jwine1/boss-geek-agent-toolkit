
## 4. `html-report/SKILL.md`

```markdown
---
name: html-report
description: |
  汇总岗位搜索、岗位评分、JD 分析、简历建议和面试准备结果，生成本地 HTML 求职分析报告。

  本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 6），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
---

# HTML 求职分析报告

生成独立 HTML 文件，将岗位搜索结果、评分、风险提示、简历建议和面试准备材料汇总为可视化报告。

## 前提条件

- 已生成 `output/jobs.json`
- 已生成 `output/scores.json`
- 如需要完整报告，应已有 `output/details/`、`output/tailored_resumes/` 或 `output/interview/`
- 已存在 `html-report/scripts/generate_report.py`

## 用法

```bash
python html-report/scripts/generate_report.py