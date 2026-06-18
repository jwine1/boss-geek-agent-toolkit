# boss-geek-agent-toolkit

一个面向 BOSS 直聘求职端的 AI Agent 工具包，用于辅助完成岗位搜索、岗位匹配、JD 分析、简历优化建议、面试准备和本地 HTML 求职报告生成。

本项目不是自动投递工具，也不是自动沟通工具。它的定位是：帮助求职者更高效地理解岗位、筛选岗位、判断匹配度，并生成后续求职准备材料。

## 项目定位

在 BOSS 直聘求职过程中，用户通常会遇到几个问题：

1. 岗位数量多，人工筛选效率低；
2. JD 信息分散，难以快速判断是否适合自己；
3. 简历与岗位要求之间的匹配关系不清晰；
4. 面试准备缺少针对性；
5. 搜索、评分、详情分析、简历建议和报告整理流程割裂。

本项目通过一组 Agent Skill 和本地脚本，将上述流程拆分为可复用的工作模块，使 AI Agent 能够按照固定流程辅助求职者完成岗位分析。

## 功能概览

```text
用户输入岗位关键词 / 城市 / 求职方向
        │
        ▼
[1] 搜索岗位
        │
        ▼
[2] 岗位匹配评分
        │
        ▼
[3] 获取岗位详情
        │
        ▼
[4] 生成简历优化建议
        │
        ▼
[5] 生成面试准备材料
        │
        ▼
[6] 生成 HTML 求职分析报告
```

## 主要能力

| 模块              | 作用                                                      |
| --------------- | ------------------------------------------------------- |
| boss-geek-auto  | 项目总入口，负责编排完整求职分析流程                                      |
| boss-job-search | 调用 `boss-agent-cli` 搜索 BOSS 直聘岗位，并生成 `output/jobs.json` |
| job-matcher     | 根据求职画像和岗位信息进行岗位匹配评分                                     |
| boss-job-detail | 根据岗位 `security_id` 获取岗位详情                               |
| resume-tailor   | 根据 JD、基础简历和个人素材库生成简历修改建议                                |
| interview-prep  | 根据 JD 和个人素材生成面试准备材料                                     |
| html-report     | 汇总搜索、评分、详情、简历建议和面试准备结果，生成本地 HTML 报告                     |
| geek-profile    | 维护求职画像、基础简历和个人素材库                                       |

## 项目结构

```text
boss-geek-agent-toolkit/
├── boss-geek-auto/
│   └── SKILL.md
│
├── boss-job-search/
│   ├── SKILL.md
│   └── scripts/
│       └── run_search.py
│
├── boss-job-detail/
│   └── SKILL.md
│
├── job-matcher/
│   └── SKILL.md
│
├── resume-tailor/
│   └── SKILL.md
│
├── interview-prep/
│   └── SKILL.md
│
├── html-report/
│   ├── SKILL.md
│   └── scripts/
│       └── generate_report.py
│
├── geek-profile/
│   ├── SKILL.md
│   ├── profile.yaml
│   ├── resume_base.md
│   └── career_assets.md
│
├── requirements.txt
└── README.md
```

## 安装环境

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

当前项目依赖：

```text
boss-agent-cli
```

### 4. 检查 BOSS CLI 状态

```bash
boss status
boss doctor
```

如果尚未登录：

```bash
boss login
```

## 使用前配置

建议先完善 `geek-profile/` 下的个人资料文件。

### 1. 求职画像：`geek-profile/profile.yaml`

示例：

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

scoring_weights:
  target_roles: 30
  prefer: 20
  priority: 20
  target_city: 10
  current_stage: 10
  salary_min: 5
  avoid: 30
```

### 2. 基础简历：`geek-profile/resume_base.md`

用于存放默认简历底稿。

建议结构：

```markdown
# 默认简历底稿

## 求职方向

## 教育背景

## 核心能力

## 项目经历

## 奖项证书

## 自我评价
```

### 3. 个人素材库：`geek-profile/career_assets.md`

用于存放项目、能力、奖项、自我介绍等可复用素材。

示例结构：

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

## 基础用法

### 1. 搜索岗位

```bash
python boss-job-search/scripts/run_search.py --query "Agent实习" --city "南京" --pages 1
```

运行后会生成：

```text
output/jobs.json
output/raw/latest_p1.txt
```

`output/jobs.json` 是标准化后的岗位搜索结果，后续岗位评分、详情分析和报告生成都会读取该文件。

### 2. 使用 AI Agent 进行岗位评分

岗位搜索完成后，让支持本地文件读写和命令执行的 AI Agent 加载项目 Skill。

推荐入口：

```text
boss-geek-auto/SKILL.md
```

岗位评分会读取：

```text
geek-profile/profile.yaml
output/jobs.json
```

并生成：

```text
output/scores.json
```

评分等级说明：

| 等级 |   分数范围 | 含义     |
| -- | -----: | ------ |
| A  | 80-100 | 优先查看详情 |
| B  |  65-79 | 可以备选   |
| C  |  50-64 | 谨慎考虑   |
| D  |   0-49 | 建议跳过   |

### 3. 获取岗位详情

对高分岗位或用户指定岗位，可以根据 `security_id` 获取岗位详情。

示例命令：

```bash
boss detail <security_id>
```

岗位详情建议保存到：

```text
output/details/
```

### 4. 生成简历优化建议

AI Agent 会读取：

```text
output/details/
geek-profile/resume_base.md
geek-profile/career_assets.md
output/scores.json
```

并生成：

```text
output/tailored_resumes/
```

简历建议必须基于用户已有素材，不应虚构经历、奖项、证书、公司、实习或量化结果。

### 5. 生成面试准备材料

AI Agent 会读取：

```text
output/details/
geek-profile/career_assets.md
output/tailored_resumes/
```

并生成：

```text
output/interview/
```

输出内容包括：

```text
岗位核心要求
60 秒自我介绍
项目经历讲法
高频问题
项目追问
行为面试题
反问面试官问题
准备优先级
```

### 6. 生成 HTML 报告

```bash
python html-report/scripts/generate_report.py
```

运行后生成：

```text
output/report.html
```

Windows 下可直接打开：

```bash
start output/report.html
```

报告内容包括：

```text
搜索概况
岗位排序
推荐岗位
风险提示
岗位详情分析
简历建议
面试准备
下一步建议
```

## 输出文件说明

| 文件 / 目录                  | 说明             |
| ------------------------ | -------------- |
| output/jobs.json         | 最新一次岗位搜索结果     |
| output/raw/              | 最新一次搜索的原始输出    |
| output/scores.json       | 岗位匹配评分结果       |
| output/details/          | 岗位详情数据         |
| output/tailored_resumes/ | 简历修改建议或定制简历草稿  |
| output/interview/        | 面试准备材料         |
| output/report.html       | 本地 HTML 求职分析报告 |

## 推荐工作流

```bash
# 1. 搜索岗位
python boss-job-search/scripts/run_search.py --query "Agent实习" --city "南京" --pages 1

# 2. 让 AI Agent 读取 boss-geek-auto/SKILL.md
#    执行岗位评分、详情分析、简历建议和面试准备

# 3. 生成 HTML 报告
python html-report/scripts/generate_report.py

# 4. 打开报告
start output/report.html
```

## 设计边界

本项目只做求职者端岗位辅助，不做以下操作：

```text
不自动投递
不自动打招呼
不自动发送消息
不自动交换联系方式
不绕过登录、验证码或平台安全校验
不使用招聘者端功能
不处理候选人数据
```

所有投递、沟通、交换联系方式等操作均应由用户在 BOSS 直聘官方页面中手动完成。

## 数据边界

本项目生成的数据默认保存在本地 `output/` 目录。

使用过程中应注意：

1. 岗位搜索结果具有时效性；
2. 每次重新搜索岗位时，旧的评分、详情、报告可能需要重新生成；
3. 简历建议必须基于 `resume_base.md` 和 `career_assets.md`；
4. 不应编造用户经历、实习、证书、学历、奖项或量化结果；
5. AI 生成的岗位评分和建议仅作为辅助判断，最终求职决策由用户自行确认。

## 适用场景

本项目适合：

```text
找实习
找校招岗位
筛选 AI / Agent / Python / 大模型应用相关岗位
分析岗位 JD
判断岗位与个人经历的匹配度
根据岗位生成简历优化建议
准备针对性面试问题
生成本地求职分析报告
```

不适合：

```text
批量自动投递
自动打招呼
自动聊天沟通
招聘者端候选人管理
绕过平台限制
采集或处理非本人求职数据
```

## 常见问题

### 1. 找不到 boss 命令怎么办？

先确认是否安装了 `boss-agent-cli`：

```bash
pip install boss-agent-cli
```

再检查：

```bash
boss status
boss doctor
```

如果仍然找不到，可以在搜索时手动指定路径：

```bash
python boss-job-search/scripts/run_search.py --query "Agent实习" --city "南京" --pages 1 --boss-cmd "你的boss.exe路径"
```

### 2. 搜索结果为空怎么办？

可以检查：

```text
output/raw/latest_p1.txt
```

常见原因包括：

```text
CLI 未登录
关键词过窄
城市参数不匹配
BOSS 页面或 CLI 返回格式变化
网络异常
```

### 3. 为什么不自动投递？

本项目的目标是辅助分析和决策，不替代用户在 BOSS 直聘官方页面上的主动操作。自动投递、自动打招呼、自动发送消息和自动交换联系方式都不属于本项目范围。

### 4. HTML 报告无法生成怎么办？

请先确认已经生成评分文件：

```text
output/scores.json
```

如果只有岗位搜索结果，没有评分结果，`html-report/scripts/generate_report.py` 可能无法生成完整报告。

## 后续计划

可继续扩展的方向包括：

```text
更稳定的岗位详情结构化解析
更细的岗位风险识别规则
更完整的简历素材匹配机制
更美观的 HTML 报告模板
多岗位对比分析
求职记录追踪
投递前检查清单
```

## 免责声明

本项目仅用于个人求职辅助分析。岗位信息、公司信息和招聘状态以 BOSS 直聘官方页面实时展示为准。AI 生成的评分、建议、简历修改意见和面试准备材料仅供参考，不构成就业承诺、录用预测或职业决策保证。

用户应自行判断岗位真实性、公司资质、沟通风险和求职安全。
