---

name: boss-geek-auto
description: |
BOSS 直聘求职者端岗位分析入口 Skill。
当用户要求搜索岗位、筛选岗位、分析 JD、生成求职报告、生成简历优化建议或面试准备材料时使用。

触发场景：

* "帮我找实习" / "搜索岗位" / "筛选岗位"
* "分析这些岗位适不适合我"
* "根据 JD 给简历修改建议"
* "生成岗位分析报告"
* "帮我准备这个岗位的面试"

不触发场景：

* 非 BOSS 直聘岗位来源
* 自动投递、自动打招呼、自动沟通
* 招聘者端职位管理或候选人处理

子 Skill 说明：
boss-agent-cli、boss-job-search、job-matcher、boss-job-detail、resume-tailor、interview-prep、html-report 均为本流程的子步骤，不应作为入口直接加载。请始终先加载本 Skill 获取完整工作流，再按 Step 顺序调用子 Skill。
type: workflow
--------------

# BOSS 直聘求职者端岗位分析全流程

> 入口声明：本 Skill 是 boss-geek-agent-toolkit 项目的入口。下文子 Skill 应按本 Skill 的编排顺序调用，用于完成岗位搜索、岗位评分、JD 分析、简历建议、面试准备和报告生成。

## 流程总览

```text
用户提供求职关键词/城市/岗位方向
     │
     ▼
[Step 1] 搜索岗位 ───── 使用 skill: boss-job-search
     │
     ▼
[Step 2] 岗位评分 ───── 使用 skill: job-matcher
     │
     ▼
[Step 3] 查看详情 ───── 使用 skill: boss-job-detail
     │
     ▼
[Step 4] 简历建议 ───── 使用 skill: resume-tailor
     │
     ▼
[Step 5] 面试准备 ───── 使用 skill: interview-prep
     │
     ▼
[Step 6] 生成报告 ───── 使用 skill: html-report
```

不做：自动投递、自动打招呼、自动发送消息、自动交换联系方式。以上操作均由用户在 BOSS 直聘官方页面手动完成。

---

## 用到的 Skill 列表

|  # | Skill           | 在流程中的作用                                      |
| -: | --------------- | -------------------------------------------- |
|  1 | boss-agent-cli  | CLI 命令参考、登录、搜索、详情等基础能力说明                     |
|  2 | boss-job-search | 调用 CLI 搜索岗位，生成 `output/jobs.json`            |
|  3 | job-matcher     | 根据用户画像和岗位信息进行初筛评分，生成 `output/scores.json`    |
|  4 | boss-job-detail | 根据 `security_id` 获取岗位详情，生成 `output/details/` |
|  5 | resume-tailor   | 根据 JD、基础简历和素材库生成简历修改建议                       |
|  6 | interview-prep  | 根据 JD 和用户素材生成面试准备材料                          |
|  7 | html-report     | 汇总岗位评分、风险提示、简历建议和面试准备，生成 HTML 报告             |

---

## 输入信息

| 输入              | 说明                                    | 默认处理                                 |
| --------------- | ------------------------------------- | ------------------------------------ |
| `query`         | 岗位关键词，如 `Agent实习`、`Python实习`、`AI产品实习` | 必填或由用户意图推断                           |
| `city`          | 搜索城市                                  | 未提供时使用 profile 配置                    |
| `pages`         | 搜索页数                                  | 默认 1                                 |
| `profile`       | 求职画像配置                                | 默认读取 `geek-profile/profile.yaml`     |
| `resume_base`   | 基础简历底稿                                | 默认读取 `geek-profile/resume_base.md`   |
| `career_assets` | 项目、能力、奖项、自我介绍素材库                      | 默认读取 `geek-profile/career_assets.md` |

---

## 输出文件

| 文件                         | 说明            |
| -------------------------- | ------------- |
| `output/jobs.json`         | 岗位搜索结果        |
| `output/scores.json`       | 岗位评分结果        |
| `output/details/`          | 岗位详情数据        |
| `output/tailored_resumes/` | 简历修改建议或定制简历草稿 |
| `output/interview/`        | 面试准备材料        |
| `output/report.html`       | 岗位分析报告        |

---

## Step 0: 环境检查

执行前先参考 `boss-agent-cli` Skill 检查 CLI 是否可用。

常用命令：

```bash
boss status
boss doctor
boss schema
```

如果 CLI 未登录，提示用户执行：

```bash
boss login
```

如果存在多个 `boss.exe`，优先使用项目虚拟环境中的 CLI 路径。

---

## Step 1: 搜索岗位

执行 skill：`boss-job-search`

核心操作：

```bash
python boss-job-search/scripts/run_search.py --query "<query>" --city "<city>" --pages 1
```

输出：

```text
output/jobs.json
output/raw/
```

要求：

* 优先解析 CLI 的 JSON 输出。
* 保留 `job_id` 和 `security_id`。
* 不在本步骤做评分、简历建议或投递操作。

---

## Step 2: 岗位评分

执行 skill：`job-matcher`

输入：

```text
geek-profile/profile.yaml
output/jobs.json
```

输出：

```text
output/scores.json
```

评分重点：

* 岗位名称与目标方向是否匹配。
* 岗位描述是否符合实习、低经验、在校生或可培养要求。
* 技能关键词是否匹配。
* 是否存在明显风险词。
* 是否值得进入详情分析。

---

## Step 3: 查看岗位详情

执行 skill：`boss-job-detail`

核心操作：

```bash
boss detail <security_id>
```

或由对应脚本批量处理高分岗位。

输入：

```text
output/scores.json
```

输出：

```text
output/details/
```

要求：

* 只对高分岗位或用户指定岗位获取详情。
* 不进行无意义的大规模详情抓取。
* 保存岗位 JD、岗位职责、任职要求、福利、公司信息等字段。

---

## Step 4: 生成简历建议

执行 skill：`resume-tailor`

输入：

```text
geek-profile/resume_base.md
geek-profile/career_assets.md
output/details/
output/scores.json
```

输出：

```text
output/tailored_resumes/
```

要求：

* 简历建议必须基于用户已有素材。
* 不虚构经历、实习、奖项、证书、公司或量化结果。
* 输出应包括推荐突出经历、能力匹配点、简历修改建议和不建议强调的内容。
* 可以生成草稿，但最终是否使用由用户决定。

---

## Step 5: 生成面试准备材料

执行 skill：`interview-prep`

输入：

```text
output/details/
geek-profile/career_assets.md
```

输出：

```text
output/interview/
```

输出内容：

* 岗位核心要求。
* 可能面试问题。
* 项目经历追问。
* 行为面试问题。
* 自我介绍建议。
* 反问面试官问题。

---

## Step 6: 生成报告

执行 skill：`html-report`

核心操作：

```bash
python html-report/scripts/generate_report.py
```

输入：

```text
output/jobs.json
output/scores.json
output/details/
output/tailored_resumes/
output/interview/
```

输出：

```text
output/report.html
```

报告内容：

* 搜索关键词和城市。
* 岗位总数。
* 推荐岗位列表。
* 岗位评分与推荐理由。
* 风险岗位和风险原因。
* 建议查看详情的岗位。
* 简历修改建议入口。
* 面试准备材料入口。

---

## 文件结构

```text
boss-geek-agent-toolkit/
├── boss-agent-cli/
│   └── SKILL.md
├── boss-geek-auto/
│   └── SKILL.md
├── boss-job-search/
│   ├── SKILL.md
│   └── scripts/
│       └── run_search.py
├── boss-job-detail/
│   └── SKILL.md
├── job-matcher/
│   ├── SKILL.md
│   └── scripts/
│       └── score_jobs.py
├── resume-tailor/
│   └── SKILL.md
├── interview-prep/
│   └── SKILL.md
├── html-report/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_report.py
├── geek-profile/
│   ├── profile.yaml
│   ├── resume_base.md
│   └── career_assets.md
└── output/
    ├── jobs.json
    ├── scores.json
    ├── details/
    ├── tailored_resumes/
    ├── interview/
    └── report.html
```

---

## 重要规则

### 运行边界

* 本项目只做求职者端岗位辅助。
* 只处理用户主动发起的岗位搜索和分析任务。
* 不进行自动投递。
* 不自动打招呼。
* 不自动发送消息。
* 不自动交换联系方式。
* 不绕过登录、验证码或平台安全校验。
* 不使用招聘者端命令。
* 不处理候选人数据。

### 数据边界

* 搜索结果、岗位详情和分析报告均保存在本地 `output/` 目录。
* 简历建议必须基于 `resume_base.md` 和 `career_assets.md`。
* 不虚构用户经历。
* 不夸大项目结果。
* 不编造证书、奖项、实习或学历信息。

### 执行边界

* `boss-agent-cli` 只作为底层命令参考。
* `boss-geek-auto` 负责流程编排。
* 子 Skill 不应越权执行完整流程。
* Python 脚本只处理局部任务，不承担完整业务流程。
