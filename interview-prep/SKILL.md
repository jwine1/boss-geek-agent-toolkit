# interview-prep/SKILL.md

---

name: interview-prep
description: |
根据岗位 JD 和用户素材生成面试准备材料，包括自我介绍、项目追问、行为面试题和反问问题。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 5），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# 面试准备材料生成

读取岗位详情和个人素材库，生成针对目标岗位的面试准备文档。

## 前提条件

* 已获取目标岗位详情
* 已存在 `geek-profile/career_assets.md`
* 如需要结合简历，应先执行 `resume-tailor`

## 输入文件

| 文件                              | 用途              |
| ------------------------------- | --------------- |
| `output/details/`               | 岗位 JD、职责和任职要求   |
| `geek-profile/career_assets.md` | 项目、能力、奖项和自我介绍素材 |
| `output/tailored_resumes/`      | 简历建议或定制简历草稿，可选  |

## 输出目录

```text
output/interview/
```

## 工作流程

1. 读取目标岗位 JD
2. 提取岗位核心能力要求
3. 匹配用户素材库中的项目和能力
4. 生成自我介绍建议
5. 生成可能面试问题
6. 生成项目追问和回答要点
7. 生成反问面试官问题
8. 保存到 `output/interview/`

## 输出内容

```markdown
# 面试准备：<公司> - <岗位>

## 岗位核心要求

## 60 秒自我介绍

## 项目经历讲法

## 高频问题

## 项目追问

## 行为面试题

## 反问面试官问题

## 准备优先级
```

## 输出要求

* 回答要点必须基于用户已有素材
* 不虚构项目、实习、奖项或能力
* 不编造面试官信息
* 不承诺录用概率
* 对素材不足的部分应提示需要补充

## 不做的步骤

| 步骤         | 原因                 |
| ---------- | ------------------ |
| 自动发送消息     | 必须由用户手动完成          |
| 自动投递       | 必须由用户在官网手动完成       |
| 修改简历文件     | 交给 `resume-tailor` |
| 生成 HTML 报告 | 交给 `html-report`   |

---

# html-report/SKILL.md

---

name: html-report
description: |
汇总岗位搜索、岗位评分、JD 分析、简历建议和面试准备结果，生成本地 HTML 求职分析报告。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 6），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# HTML 求职分析报告

生成独立 HTML 文件，将岗位搜索结果、评分、风险提示、简历建议和面试准备材料汇总为可视化报告。

## 前提条件

* 已生成 `output/jobs.json`
* 已生成 `output/scores.json`
* 如需要完整报告，应已有 `output/details/`、`output/tailored_resumes/` 或 `output/interview/`
* 已存在 `html-report/scripts/generate_report.py`

## 用法

```bash
python html-report/scripts/generate_report.py
```

打开报告：

```bash
start output/report.html
```

## 输入文件

| 文件                         | 用途        |
| -------------------------- | --------- |
| `output/jobs.json`         | 岗位搜索结果    |
| `output/scores.json`       | 岗位评分结果    |
| `output/details/`          | 岗位详情，可选   |
| `output/tailored_resumes/` | 简历建议，可选   |
| `output/interview/`        | 面试准备材料，可选 |

## 输出文件

```text
output/report.html
```

## 工作流程

1. 读取岗位搜索结果
2. 读取岗位评分结果
3. 汇总推荐岗位、备选岗位和风险岗位
4. 读取岗位详情、简历建议和面试准备材料
5. 渲染为独立 HTML 报告
6. 保存到 `output/report.html`

## 报告内容

| 模块   | 内容               |
| ---- | ---------------- |
| 搜索概况 | 关键词、城市、岗位数量、生成时间 |
| 推荐岗位 | Top 岗位、评分、推荐理由   |
| 风险提示 | 风险岗位、风险原因        |
| 详情分析 | JD 摘要、技能要求、岗位职责  |
| 简历建议 | 推荐突出经历、修改建议      |
| 面试准备 | 高频问题、项目追问、反问问题   |
| 下一步  | 查看详情、修改简历、手动投递   |

## 输出要求

* 生成独立 HTML 文件
* 不把完整报告直接输出到聊天窗口
* 原始 JSON 不应暴露为主报告内容
* 报告应便于本地打开和人工决策
* 如果某些输入文件不存在，应降级生成已有数据报告

## 不做的步骤

| 步骤   | 原因                   |
| ---- | -------------------- |
| 搜索岗位 | 交给 `boss-job-search` |
| 岗位评分 | 交给 `job-matcher`     |
| 简历建议 | 交给 `resume-tailor`   |
| 面试准备 | 交给 `interview-prep`  |
| 自动投递 | 必须由用户在官网手动完成         |
