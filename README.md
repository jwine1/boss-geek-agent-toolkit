# boss-geek-agent-toolkit

> 🧑‍💻 BOSS 直聘求职者端 AI Agent 技能包，基于 `boss-agent-cli`，辅助完成岗位搜索、岗位匹配、JD 分析、简历优化建议、面试准备和本地 HTML 求职报告生成。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Agent Skills](https://img.shields.io/badge/Agent-Skills-purple)]()
[![BOSS](https://img.shields.io/badge/BOSS-Geek%20Side-orange)]()

## 🎯 功能概述

```text
你想找岗位
   → AI 搜索岗位
   → AI 根据你的 profile 评分
   → AI 分析 JD
   → AI 生成简历建议和面试准备
   → 输出本地 HTML 求职报告
```

一句话：**让 AI Agent 帮求职者更快筛岗位、看 JD、改简历、准备面试。**

> 本项目不是自动投递工具，也不是自动沟通工具。所有投递、打招呼和沟通都必须由用户在 BOSS 直聘官方页面手动完成。

---

## 📦 Skill 一览

> 🚪 `boss-geek-auto` 是唯一入口，其余 Skill 是子步骤。使用时建议始终从 `boss-geek-auto` 开始。

|  #  | Skill              |   角色   | 作用                         |
| :-: | ------------------ | :----: | -------------------------- |
|  0  | **boss-geek-auto** |  🚪 入口 | 编排完整求职分析流程                 |
|  1  | boss-job-search    | Step 1 | 搜索岗位并生成 `output/jobs.json` |
|  2  | job-matcher        | Step 2 | 根据 `profile.yaml` 进行岗位匹配评分 |
|  3  | boss-job-detail    | Step 3 | 获取高分岗位 JD 详情               |
|  4  | resume-tailor      | Step 4 | 生成简历优化建议                   |
|  5  | interview-prep     | Step 5 | 生成面试准备材料                   |
|  6  | html-report        | Step 6 | 生成本地 HTML 求职报告             |
|  7  | geek-profile       |  📁 资料 | 维护求职画像、简历底稿和个人素材库          |

---

## 🔁 工作流

```text
用户：「帮我分析这些岗位」
     │
     ▼
┌───────────────────────────────────────────────┐
│              boss-geek-auto（总控入口）          │
│                                               │
│  [Step 1] boss-job-search  → 搜索岗位           │
│  [Step 2] job-matcher      → 匹配评分           │
│  [Step 3] boss-job-detail  → 获取 JD           │
│  [Step 4] resume-tailor    → 简历建议           │
│  [Step 5] interview-prep   → 面试准备           │
│  [Step 6] html-report      → 生成报告           │
└───────────────────────────────────────────────┘
     │
     ▼
📊 output/report.html
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/jwine1/boss-geek-agent-toolkit.git
cd boss-geek-agent-toolkit
```

### 2. 创建虚拟环境

Windows：

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

当前核心依赖：

```text
boss-agent-cli
```

### 4. 登录 BOSS CLI

```bash
boss login
boss status
```

如果 `boss status` 显示不完整，但 `boss search` 能正常返回岗位，通常可以继续使用。

---

## 🧠 与 Agent 配合使用

本项目主要面向支持本地文件读写、命令执行和 Skill 加载能力的 AI Agent，例如：

```text
Claude Code
OpenClaw
其他本地 Agent 运行环境
```

推荐让 Agent 从入口 Skill 开始：

```text
请读取 boss-geek-auto/SKILL.md，帮我搜索并分析 <城市> 的 <岗位关键词> 岗位，
完成岗位评分、JD 分析、简历建议、面试准备和 HTML 报告生成。
```

如果你的 Agent 支持项目级 Skill，可将 Skill 放入对应的 skills 目录后触发入口 Skill。

---

## ⚙️ 手动运行岗位搜索

岗位搜索底层由脚本完成：

```bash
python boss-job-search/scripts/run_search.py --query "<岗位关键词>" --city "<城市>" --pages 1
```

示例：

```bash
python boss-job-search/scripts/run_search.py --query "Agent实习" --city "南京" --pages 1
```

输出：

```text
output/jobs.json
output/raw/latest_p1.txt
```

`output/jobs.json` 始终表示最新一次岗位搜索结果。

---

## 👤 配置求职画像

使用前建议完善：

```text
geek-profile/profile.yaml
geek-profile/resume_base.md
geek-profile/career_assets.md
```

### `profile.yaml` 示例

```yaml
target_city: 南京

target_roles:
  - Agent实习
  - Python实习
  - 大模型应用实习

salary_min: 0

prefer:
  - Agent
  - Python
  - RAG
  - 自动化

avoid:
  - 纯销售
  - 电销
  - 培训贷
  - 收费培训

search_pages: 1
```

说明：

| 文件                 | 作用                  |
| ------------------ | ------------------- |
| `profile.yaml`     | 求职方向、城市、偏好、规避项和评分配置 |
| `resume_base.md`   | 基础简历底稿              |
| `career_assets.md` | 项目、能力、奖项、自我介绍等素材    |

---

## 📊 输出文件

| 文件 / 目录                    | 说明             |
| -------------------------- | -------------- |
| `output/jobs.json`         | 最新一次岗位搜索结果     |
| `output/scores.json`       | 岗位匹配评分结果       |
| `output/details/`          | 岗位详情数据         |
| `output/tailored_resumes/` | 简历优化建议         |
| `output/interview/`        | 面试准备材料         |
| `output/report.html`       | 本地 HTML 求职分析报告 |

---

## 🛡️ 安全边界

本项目只做求职辅助分析。

✅ 支持：

* 岗位搜索
* 岗位评分
* JD 分析
* 简历建议
* 面试准备
* 本地报告生成

❌ 不做：

* 自动投递
* 自动打招呼
* 自动发送消息
* 自动交换联系方式
* 绕过登录、验证码或平台安全校验
* 使用招聘者端功能
* 处理候选人数据

---

## 📁 项目结构

```text
boss-geek-agent-toolkit/
├── boss-geek-auto/          # 🚪 总控入口
│   └── SKILL.md
│
├── boss-job-search/         # Step 1：岗位搜索
│   ├── SKILL.md
│   └── scripts/run_search.py
│
├── job-matcher/             # Step 2：岗位评分
│   └── SKILL.md
│
├── boss-job-detail/         # Step 3：JD 详情
│   ├── SKILL.md
│   └── scripts/run_detail.py
├── resume-tailor/           # Step 4：简历建议
│   └── SKILL.md
│
├── interview-prep/          # Step 5：面试准备
│   └── SKILL.md
│
├── html-report/             # Step 6：HTML 报告
│   ├── SKILL.md
│   └── scripts/generate_report.py
│
├── geek-profile/            # 👤 用户画像与素材
│   ├── SKILL.md
│   ├── profile.yaml
│   ├── resume_base.mdgit add README.md
git commit -m "Add project README"
git push origin maingit add README.md
git commit -m "Add project README"
git push origin main
│   └── career_assets.md
│
├── requirements.txt
└── README.md
```

---

## ❓ FAQ

### 1. 找不到 `boss` 命令怎么办？

先确认依赖已安装：

```bash
pip install boss-agent-cli
```

再检查：

```bash
boss status
boss doctor
```

也可以在搜索时手动指定路径：

```bash
python boss-job-search/scripts/run_search.py --query "<岗位关键词>" --city "<城市>" --pages 1 --boss-cmd "<boss.exe路径>"
```

### 2. 搜索结果为空怎么办？

检查：

```text
output/raw/latest_p1.txt
```

常见原因：

```text
CLI 未登录
关键词过窄
城市参数不匹配
网络异常
CLI 返回格式变化
```

### 3. 为什么不自动投递？

本项目的定位是辅助分析和决策，不替代用户在 BOSS 直聘官方页面上的主动操作。

---

## 🧭 Roadmap

* [ ] 更稳定的岗位详情结构化解析
* [ ] CLI + CDP 双通道详情获取
* [ ] 更完善的素材库匹配机制
* [ ] 更美观的 HTML 报告模板
* [ ] 多岗位对比分析
* [ ] 求职记录追踪
* [ ] 投递前检查清单

---

## 📄 License

MIT

---

## ⚠️ Disclaimer

本项目仅用于个人求职辅助分析。岗位信息、公司信息和招聘状态以 BOSS 直聘官方页面实时展示为准。AI 生成的评分、建议、简历修改意见和面试准备材料仅供参考，不构成就业承诺、录用预测或职业决策保证。

用户应自行判断岗位真实性、公司资质、沟通风险和求职安全。
