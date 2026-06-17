---
name: boss-agent-cli
description: |
BOSS 直聘求职者端 CLI 命令参考手册。
本 Skill 是 boss-geek-auto 编排流程的底层命令参考，不作为入口直接加载。
当前项目仅面向求职者账号，聚焦岗位搜索、岗位详情查看、本地候选池、岗位分析、简历优化和面试准备。
type: reference
---------------

# boss-agent-cli

> AI Agent 专用的 BOSS 直聘求职者端本地辅助 CLI 工具参考。当前项目默认低风险模式：本地辅助、只读优先、用户主动触发、不规避平台风控、不自动投递、不自动打招呼、不交换联系方式、不调用招聘者端能力。

## 0. 项目定位

本 Skill 服务于 `boss-geek-agent-toolkit`，用于约束 Agent 如何调用 `boss-agent-cli`。

当前项目身份是：

```text
求职者账号
```

当前项目目标是：

```text
岗位搜索
→ 岗位 JSON 保存
→ 岗位匹配评分
→ JD 详情分析
→ 简历素材匹配
→ 定制简历建议
→ 面试准备
→ HTML 求职分析报告
```

当前项目不是：

```text
招聘者端工具
HR 简历筛选工具
自动投递工具
自动打招呼工具
绕过平台安全校验工具
```

---

## 1. 安装与环境检查

推荐安装：

```powershell
python -m pip install boss-agent-cli
```

或：

```powershell
uv tool install boss-agent-cli
```

如需要浏览器登录链路，可安装浏览器依赖：

```powershell
python -m patchright install chromium
```

环境检查：

```powershell
boss doctor
```

检查版本：

```powershell
boss --version
```

检查命令位置：

```powershell
where boss
```

---

## 2. 登录流程

### 2.1 检查登录态

```powershell
boss status
```

如果 `boss status` 显示已登录，但 `boss search` 无法正常返回岗位，应以 `boss search` 的实际结果为准。

当前项目中曾出现：

```text
logged in as None
```

但 `boss search` 仍可正常返回岗位。因此该状态不是第一阶段阻塞点。

### 2.2 登录

```powershell
boss login
```

登录只用于用户主动授权的求职者端辅助操作。

本项目第一阶段不主动使用 CDP、Cookie 注入、浏览器自动化或平台接口逆向。

---

## 3. 角色边界

### 3.1 默认角色

求职者模式是默认模式：

```powershell
boss search "中台管培生" --city 南京
```

如需显式声明，可使用：

```powershell
boss --role candidate search "中台管培生" --city 南京
```

但第一版项目通常不需要显式加 `--role candidate`。

### 3.2 禁止使用招聘者模式

严禁使用：

```powershell
boss --role recruiter status
boss --role recruiter me
boss --role recruiter hr jobs list
boss hr jobs list
boss hr applications
boss hr candidates
boss hr resume
boss hr chat
boss hr reply
boss hr request-resume
```

原因：

```text
当前账号是求职者账号，不是招聘者账号。
项目目标是岗位筛选与求职辅助，不处理候选人数据。
```

---

## 4. 允许命令

### 4.1 查看 CLI Schema

Agent 在不确定命令参数时，可先调用：

```powershell
boss schema
```

用途：

```text
查看当前 CLI 暴露的命令、参数和 JSON 输出结构。
```

### 4.2 搜索岗位

基础搜索：

```powershell
boss search "中台管培生" --city 南京
```

指定福利搜索：

```powershell
boss search "中台管培生" --city 南京 --welfare "双休,五险一金"
```

指定页码：

```powershell
boss search "中台管培生" --city 南京 --page 2
```

典型用途：

```text
岗位发现
福利筛选
生成 output/jobs.json 的原始数据来源
```

### 4.3 查看当前搜索结果中的某个岗位

```powershell
boss show 1
```

说明：

```text
show 依赖最近一次 search 的上下文。
适合临时查看搜索结果第 N 条岗位。
不适合作为长期稳定引用。
```

### 4.4 查看岗位详情

```powershell
boss detail <security_id>
```

说明：

```text
detail 依赖 search 返回的 security_id。
比 boss show 1 更适合后续 JD 详情分析。
```

### 4.5 加入本地候选池

```powershell
boss shortlist add <security_id> <job_id>
```

说明：

```text
shortlist 是本地整理能力，不等于投递。
是否加入候选池必须由用户明确触发。
```

查看本地候选池：

```powershell
boss shortlist list
```

移除本地候选岗位：

```powershell
boss shortlist remove <security_id>
```

### 4.6 本地统计

```powershell
boss stats
```

用途：

```text
查看本地缓存、候选池和整理结果。
```

### 4.7 导出岗位

```powershell
boss export "中台管培生" --city 南京 --count 50 -o jobs.csv
```

说明：

```text
可用于本地分析。
第一版项目优先使用 search JSON，不强依赖 export。
```

### 4.8 AI 求职增强命令

CLI 可能提供以下 AI 辅助能力：

```powershell
boss ai analyze-jd
boss ai polish
boss ai optimize
boss ai interview-prep
boss ai chat-coach
```

使用原则：

```text
仅用于 JD 分析、简历润色、简历优化、面试准备和沟通建议。
不得用于自动投递、自动打招呼、自动发送消息或交换联系方式。
```

第一版项目优先由 Agent 根据 `career_assets.md`、`resume_base.md` 和 JD 文本生成建议，不强依赖 CLI 内置 AI 命令。

---

## 5. 禁止命令与禁止行为

### 5.1 禁止自动投递

禁止：

```powershell
boss apply
```

规则：

```text
所有投递动作必须由用户本人回到 BOSS 直聘官网手动完成。
```

### 5.2 禁止自动打招呼

禁止：

```powershell
boss greet
boss batch-greet
```

规则：

```text
Agent 可以生成沟通建议，但不得自动发送。
```

### 5.3 禁止自动交换联系方式

禁止：

```powershell
boss exchange
```

规则：

```text
联系方式交换必须由用户本人在官方页面手动完成。
```

### 5.4 禁止聊天记录与消息自动化

禁止：

```powershell
boss chat
boss chatmsg
boss chat-summary
boss follow-up
boss digest
boss ai reply
```

规则：

```text
第一版项目不读取聊天记录，不总结聊天记录，不自动回复消息。
Agent 可根据用户手动提供的上下文生成沟通建议。
```

### 5.5 禁止招聘者端能力

禁止：

```powershell
boss hr applications
boss hr candidates
boss hr resume
boss hr chat
boss hr reply
boss hr request-resume
boss hr jobs list
boss hr jobs online
boss hr jobs offline
```

规则：

```text
当前项目不处理候选人数据，不下载简历，不管理招聘职位。
```

### 5.6 禁止绕过平台安全校验

禁止：

```text
绕过验证码
绕过登录限制
绕过风控
批量触达
批量投递
非用户主动触发的数据抓取
```

---

## 6. 输出协议

`boss-agent-cli` 的标准输出约定：

```text
stdout: JSON 结构化数据
stderr: 日志和进度信息
exit 0: 成功
exit 1: 失败
```

典型 JSON 信封：

```json
{
  "ok": true,
  "schema_version": "1.0",
  "command": "search",
  "data": [],
  "pagination": {
    "page": 1,
    "has_more": true,
    "total": 15
  },
  "error": null,
  "hints": {
    "next_actions": [
      "boss detail <security_id>"
    ]
  }
}
```

Agent 和脚本必须优先解析 JSON。

如果 stdout 前后混入提示文本，应从第一个 `{` 到最后一个 `}` 截取 JSON，再尝试解析。

---

## 7. 当前项目推荐调用方式

### 7.1 岗位搜索

```powershell
python boss-job-search/scripts/run_search.py --query "中台管培生" --city 南京 --pages 1 --boss-cmd "C:\Users\j\.local\bin\boss.exe"
```

输出：

```text
output/jobs.json
output/raw/search_raw_*.txt
```

### 7.2 岗位评分

```powershell
python job-matcher/scripts/score_jobs.py
```

输出：

```text
output/scores.json
```

### 7.3 报告生成

```powershell
python html-report/scripts/generate_report.py
```

输出：

```text
output/report.html
```

### 7.4 打开报告

```powershell
start output\report.html
```

---

## 8. 与 boss-geek-auto 的关系

本 Skill 是底层 CLI 命令参考，不作为主入口。

主入口应是：

```text
boss-geek-auto/SKILL.md
```

`boss-geek-auto` 在需要调用 BOSS CLI 时，应先参考本 Skill 的边界规则，再调用对应子 Skill：

```text
boss-job-search
job-matcher
boss-job-detail
resume-tailor
interview-prep
html-report
```

---

## 9. 与 boss-job-search 的关系

`boss-job-search` 负责把 CLI 搜索结果转成项目内部统一 JSON 文件。

推荐流程：

```text
用户输入岗位关键词和城市
→ boss-job-search 调用 boss search
→ run_search.py 解析 JSON
→ 保存 output/jobs.json
```

本 Skill 只提供 CLI 命令约束，不直接处理文件落盘。

---

## 10. 与 boss-job-detail 的关系

`boss-job-detail` 负责读取高分岗位的 `security_id`，再调用：

```powershell
boss detail <security_id>
```

输出岗位详情到：

```text
output/details/
```

第一版项目中，详情抓取应只针对高分岗位，例如：

```text
A 级岗位
Top 3 岗位
用户明确指定的岗位
```

不得无意义批量抓取大量详情。

---

## 11. 与 resume-tailor 的关系

`resume-tailor` 不直接搜索岗位。

它只读取：

```text
geek-profile/resume_base.md
geek-profile/career_assets.md
output/details/*.json
output/scores.json
```

然后生成：

```text
定制简历建议
项目经历匹配建议
自我介绍版本
面试表达建议
```

简历内容必须基于用户已有素材，不得虚构经历、奖项、公司、实习、证书或量化结果。

---

## 12. 与 interview-prep 的关系

`interview-prep` 不调用投递、沟通或聊天命令。

它只根据 JD 和用户素材生成：

```text
岗位核心要求
可能追问问题
项目追问
行为面试题
反问面试官问题
回答策略
```

---

## 13. 第一阶段最小命令集合

第一阶段只允许使用：

```powershell
boss doctor
boss status
boss login
boss schema
boss search "岗位关键词" --city 城市
boss search "岗位关键词" --city 城市 --welfare "双休,五险一金"
boss show 1
boss detail <security_id>
```

第一阶段暂不使用：

```powershell
boss shortlist add
boss export
boss ai optimize
boss ai polish
boss ai interview-prep
```

原因：

```text
第一阶段目标是跑通岗位搜索、岗位评分和 HTML 报告。
候选池、导出和 AI 能力放到第二阶段。
```

---

## 14. 第二阶段可扩展命令集合

第二阶段可按用户明确要求使用：

```powershell
boss shortlist add <security_id> <job_id>
boss shortlist list
boss shortlist remove <security_id>
boss stats
boss export "岗位关键词" --city 城市 --count 50 -o jobs.csv
boss ai analyze-jd
boss ai polish
boss ai optimize
boss ai interview-prep
boss ai chat-coach
```

但仍然禁止：

```powershell
boss apply
boss greet
boss batch-greet
boss exchange
boss chat
boss chatmsg
boss chat-summary
boss ai reply
boss hr *
```

---

## 15. 错误处理原则

### 15.1 登录失败

如果 `boss search` 返回未登录或认证失败：

```text
提示用户运行 boss login。
不要尝试绕过登录。
不要自行注入 Cookie。
不要自动启动批量浏览器流程。
```

### 15.2 命令不存在

如果出现：

```text
Unknown command
Unknown skill
```

处理方式：

```text
先运行 boss schema 查看当前 CLI 支持能力。
再根据 schema 调整命令。
不要猜测 recruiter / hr 命令。
```

### 15.3 boss 命令版本不一致

如果出现：

```text
pip 安装版本与 boss --version 不一致
```

处理方式：

```text
显式指定 boss.exe 路径。
优先使用当前项目 .venv 下的 boss.exe。
```

示例：

```powershell
python boss-job-search/scripts/run_search.py --query "中台管培生" --city 南京 --pages 1 --boss-cmd "E:\boss-geek-agent-toolkit\.venv\Scripts\boss.exe"
```

或：

```powershell
python boss-job-search/scripts/run_search.py --query "中台管培生" --city 南京 --pages 1 --boss-cmd "C:\Users\j\.local\bin\boss.exe"
```

### 15.4 JSON 解析失败

处理方式：

```text
保留原始 stdout/stderr 到 output/raw/
优先查看原始输出是否仍是 JSON 信封。
如果 CLI 输出变更，应先修改 run_search.py 的解析适配层。
```

---

## 16. 安全与合规规则

Agent 必须遵守：

```text
只做求职者端。
只做本地辅助。
只读优先。
用户主动触发。
不自动投递。
不自动打招呼。
不自动交换联系方式。
不读取或处理招聘者候选人数据。
不绕过平台风控。
不进行大规模批量抓取。
```

当用户要求敏感动作时，Agent 应给出替代方案：

```text
可以生成投递建议，但不能替你自动投递。
可以生成打招呼话术，但不能替你自动发送。
可以生成面试准备材料，但不能读取或自动处理聊天记录。
可以整理岗位候选池，但最终操作应由你在官方页面确认。
```

---

## 17. 推荐给 Agent 的调用策略

Agent 调用本 Skill 时，应按以下顺序执行：

```text
1. 确认用户需求是否属于求职者端岗位辅助。
2. 如不确定 CLI 能力，先运行 boss schema。
3. 如需要登录态，运行 boss status。
4. 如未登录，提示用户运行 boss login。
5. 搜索岗位时调用 boss-job-search，而不是直接堆命令。
6. 分析岗位时读取 output/jobs.json 和 output/scores.json。
7. 需要 JD 时，只对高分岗位调用 boss detail。
8. 生成简历建议时使用 career_assets.md 和 resume_base.md。
9. 投递、沟通、联系方式交换必须让用户回到官网手动完成。
```

---

## 18. 当前项目标准工作流

```text
boss-geek-auto
→ boss-job-search
→ job-matcher
→ boss-job-detail
→ resume-tailor
→ interview-prep
→ html-report
```

其中 CLI 主要负责：

```text
boss search
boss show
boss detail
```

Agent 主要负责：

```text
意图理解
Skill 编排
岗位分析
简历素材匹配
简历建议生成
面试准备
报告解释
```

Python 脚本主要负责：

```text
JSON 解析
本地文件保存
规则评分
HTML 渲染
```

不得把完整业务流程全部堆进一个 Python 脚本。
