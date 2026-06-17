# geek-profile/SKILL.md

---

name: geek-profile
description: |
管理求职画像、基础简历和个人素材库，为岗位评分、简历建议和面试准备提供本地资料。

本 Skill 是 boss-geek-auto 编排流程的资料子步骤，通常被 job-matcher、resume-tailor 和 interview-prep 引用，不应作为入口 Skill 直接加载。
type: reference
---------------

# 求职者资料配置

本 Skill 负责维护本地求职资料，包括求职画像、基础简历和个人素材库。岗位搜索和评分读取求职画像，简历建议和面试准备读取基础简历与素材库。

## 文件结构

```text
geek-profile/
├── SKILL.md
├── profile.yaml
├── resume_base.md
└── career_assets.md
```

## 文件说明

| 文件                 | 用途                    |
| ------------------ | --------------------- |
| `profile.yaml`     | 求职方向、城市、岗位偏好、风险词和评分配置 |
| `resume_base.md`   | 默认简历底稿                |
| `career_assets.md` | 项目、能力、奖项、自我介绍等素材库     |

## profile.yaml 格式

```yaml
target_city: 南京

target_roles:
  - Agent实习
  - AI Agent实习
  - Python实习
  - 大模型应用实习

salary_min: 0

prefer:
  - Agent
  - AI
  - 大模型
  - RAG
  - Python
  - 自动化
  - 实习
  - 在校生

avoid:
  - 纯销售
  - 电销
  - 培训贷
  - 收费培训
  - 长期无薪

search_pages: 1
```

## resume_base.md 格式

```markdown
# 默认简历底稿

## 求职方向

## 教育背景

## 核心能力

## 项目经历

## 奖项证书

## 自我评价
```

## career_assets.md 格式

```markdown
# 个人素材库

## 类型：项目
名称：
标签：
适配岗位：
证明能力：
经历描述：
可用于简历的表述：
面试可展开点：

## 类型：能力
名称：
标签：
证明能力：
可用于简历的表述：

## 类型：奖项
名称：
级别：
时间：
说明：

## 类型：自我介绍
名称：
内容：
```

## 使用规则

* `profile.yaml` 用于岗位搜索和岗位评分
* `resume_base.md` 用于生成简历建议或简历草稿
* `career_assets.md` 用于匹配 JD、生成经历表达和面试准备材料
* 简历建议必须基于已有素材
* 不虚构经历、奖项、证书、实习、学历或量化结果

## 不做的步骤

| 步骤   | 原因                   |
| ---- | -------------------- |
| 搜索岗位 | 交给 `boss-job-search` |
| 岗位评分 | 交给 `job-matcher`     |
| 获取详情 | 交给 `boss-job-detail` |
| 生成报告 | 交给 `html-report`     |

---

# resume-tailor/SKILL.md

---

name: resume-tailor
description: |
根据岗位 JD、基础简历和个人素材库生成简历修改建议或定制简历草稿。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 4），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# 简历定制建议

读取岗位详情、基础简历和个人素材库，分析 JD 要求与用户素材之间的匹配关系，输出简历修改建议或定制简历草稿。

## 前提条件

* 已获取目标岗位详情
* 已存在 `geek-profile/resume_base.md`
* 已存在 `geek-profile/career_assets.md`

## 输入文件

| 文件                              | 用途               |
| ------------------------------- | ---------------- |
| `output/details/`               | 岗位 JD 和岗位详情      |
| `geek-profile/resume_base.md`   | 基础简历底稿           |
| `geek-profile/career_assets.md` | 项目、能力、奖项和自我介绍素材库 |
| `output/scores.json`            | 岗位评分和推荐理由        |

## 输出目录

```text
output/tailored_resumes/
```

## 工作流程

1. 读取目标岗位 JD
2. 提取岗位关键词、职责和任职要求
3. 读取基础简历
4. 读取个人素材库
5. 匹配最相关的项目、能力、奖项和自我介绍素材
6. 生成简历修改建议或定制简历草稿
7. 保存到 `output/tailored_resumes/`

## 输出内容

```markdown
# 简历建议：<公司> - <岗位>

## JD 核心关键词

## 推荐突出经历

## 推荐突出能力

## 建议弱化内容

## 简历修改建议

## 可替换表述

## 风险提示
```

## 输出要求

* 必须基于 `resume_base.md` 和 `career_assets.md`
* 不虚构经历、奖项、证书、公司、实习或学历
* 不编造量化结果
* 可以优化表达，但不能改变事实
* 对缺失素材应明确提示“需要补充”
* 最终投递简历由用户自行确认

## 不做的步骤

| 步骤       | 原因                   |
| -------- | -------------------- |
| 搜索岗位     | 交给 `boss-job-search` |
| 岗位评分     | 交给 `job-matcher`     |
| 自动投递     | 必须由用户在官网手动完成         |
| 自动发送沟通内容 | 必须由用户手动发送            |
