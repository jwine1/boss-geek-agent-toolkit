
## 3. `resume-tailor/SKILL.md`

```markdown
---
name: resume-tailor
description: |
  根据岗位 JD、基础简历和个人素材库生成简历修改建议或定制简历草稿。

  本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 4），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
---

# 简历定制建议

读取岗位详情、基础简历和个人素材库，分析 JD 要求与用户素材之间的匹配关系，输出简历修改建议或定制简历草稿。

## 前提条件

- 已获取目标岗位详情
- 已存在 `geek-profile/resume_base.md`
- 已存在 `geek-profile/career_assets.md`

## 输入文件

| 文件 | 用途 |
|---|---|
| `output/details/` | 岗位 JD 和岗位详情 |
| `geek-profile/resume_base.md` | 基础简历底稿 |
| `geek-profile/career_assets.md` | 项目、能力、奖项和自我介绍素材库 |
| `output/scores.json` | 岗位评分和推荐理由 |

## 输出目录

```text
output/tailored_resumes/