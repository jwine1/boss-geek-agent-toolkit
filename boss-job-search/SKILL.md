# boss-job-search/SKILL.md

---

name: boss-job-search
description: |
调用 boss-agent-cli 搜索 BOSS 直聘岗位，并将搜索结果标准化保存为本地 JSON。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 1），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# BOSS 直聘岗位搜索

通过 `boss search` 搜索岗位，解析 CLI 返回的 JSON 数据，生成统一格式的 `output/jobs.json`，供后续岗位评分、JD 分析和报告生成使用。

## 前提条件

* 已安装 `boss-agent-cli`
* CLI 已登录或 `boss search` 可正常返回岗位
* 当前项目虚拟环境可运行 Python
* 已存在 `boss-job-search/scripts/run_search.py`

## 用法

```bash
python boss-job-search/scripts/run_search.py --query "<岗位关键词>" --city "<城市>" --pages 1
```

如需要指定 boss 命令路径：

```bash
python boss-job-search/scripts/run_search.py --query "<岗位关键词>" --city "<城市>" --pages 1 --boss-cmd "<boss.exe路径>"
```

示例：

```bash
python boss-job-search/scripts/run_search.py --query "Agent实习" --city "南京" --pages 1
```

## 工作流程

1. 根据用户输入确定 `query`、`city` 和 `pages`
2. 调用 `boss search <query> --city <city>`
3. 保存原始 stdout/stderr 到 `output/raw/`
4. 优先解析 CLI JSON 输出
5. 提取并标准化岗位字段
6. 输出 `output/jobs.json`

## 输出格式

```json
{
  "query": "Agent实习",
  "city": "南京",
  "pages": 1,
  "job_count": 15,
  "jobs": [
    {
      "page": 1,
      "index": 1,
      "job_id": "",
      "security_id": "",
      "title": "",
      "company": "",
      "salary": "",
      "exp": "",
      "edu": "",
      "city": "",
      "district": "",
      "skills": [],
      "welfare": [],
      "industry": "",
      "scale": "",
      "stage": "",
      "boss_name": "",
      "boss_title": "",
      "boss_active": "",
      "greeted": false,
      "raw_text": "",
      "show_command": "boss show 1",
      "detail_command": "boss detail <security_id>"
    }
  ],
  "errors": []
}
```

## 技术要点

* `stdout` 优先按 JSON 解析
* 如果 stdout 前后混入提示文本，从第一个 `{` 到最后一个 `}` 截取
* `security_id` 必须保留，供 `boss-job-detail` 使用
* `show_command` 只适合查看最近一次搜索结果
* `detail_command` 更适合稳定获取 JD

## 不做的步骤

| 步骤        | 原因                   |
| --------- | -------------------- |
| 自动投递      | 必须由用户在官网手动完成         |
| 自动打招呼     | 必须由用户在官网手动完成         |
| 岗位评分      | 交给 `job-matcher`     |
| JD 详情分析   | 交给 `boss-job-detail` |
| 简历修改建议    | 交给 `resume-tailor`   |
| HTML 报告生成 | 交给 `html-report`     |

---

# job-matcher/SKILL.md

---

name: job-matcher
description: |
根据用户求职画像和岗位搜索结果进行初筛评分，输出岗位推荐等级和风险提示。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 2），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# 岗位匹配评分

读取 `geek-profile/profile.yaml` 和 `output/jobs.json`，对岗位进行规则化评分，生成 `output/scores.json`，供后续岗位详情分析和报告生成使用。

## 前提条件

* 已生成 `output/jobs.json`
* 已配置 `geek-profile/profile.yaml`
* 已存在 `job-matcher/scripts/score_jobs.py`

## 用法

```bash
python job-matcher/scripts/score_jobs.py
```

## 输入文件

| 文件                          | 用途                  |
| --------------------------- | ------------------- |
| `geek-profile/profile.yaml` | 求职方向、城市、偏好、风险词和评分配置 |
| `output/jobs.json`          | 岗位搜索结果              |

## 工作流程

1. 读取用户求职画像
2. 读取岗位搜索结果
3. 对岗位标题、公司、薪资、经验、学历、技能、福利和原始文本进行匹配
4. 计算岗位匹配分
5. 标记推荐等级
6. 输出推荐理由和风险提示
7. 保存到 `output/scores.json`

## 评分维度

| 维度   | 说明                                   |
| ---- | ------------------------------------ |
| 岗位方向 | 岗位名称或描述是否命中目标方向                      |
| 技能匹配 | 是否命中 Python、AI、Agent、RAG、LLM、自动化等关键词 |
| 经验要求 | 是否接受实习生、在校生、低经验或无经验可培养               |
| 城市匹配 | 是否符合目标城市或远程要求                        |
| 薪资   | 仅作为参考，不作为唯一筛选标准                      |
| 福利   | 作为辅助加分项                              |
| 风险词  | 命中纯销售、电销、培训贷、收费培训、长期无薪等风险项扣分         |

## 输出格式

```json
{
  "generated_at": "2026-01-01 12:00:00",
  "job_count": 15,
  "scores": [
    {
      "index": 1,
      "job_id": "",
      "security_id": "",
      "title": "",
      "company": "",
      "salary": "",
      "score": 82,
      "level": "A",
      "reasons": [
        "岗位名称命中目标方向",
        "描述中包含 AI / Agent 相关关键词"
      ],
      "risks": []
    }
  ]
}
```

## 推荐等级

| 等级 | 含义     |
| -- | ------ |
| A  | 优先查看详情 |
| B  | 可以备选   |
| C  | 谨慎考虑   |
| D  | 跳过     |

## 不做的步骤

| 步骤         | 原因                   |
| ---------- | -------------------- |
| 重新搜索岗位     | 交给 `boss-job-search` |
| 获取 JD 详情   | 交给 `boss-job-detail` |
| 生成简历建议     | 交给 `resume-tailor`   |
| 生成面试材料     | 交给 `interview-prep`  |
| 生成 HTML 报告 | 交给 `html-report`     |

---

# boss-job-detail/SKILL.md

---

name: boss-job-detail
description: |
根据岗位 security_id 获取 BOSS 直聘岗位详情，用于 JD 分析、简历建议和面试准备。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 3），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# BOSS 直聘岗位详情获取

通过 `boss detail <security_id>` 获取岗位详情，保存岗位职责、任职要求、技能关键词、公司信息等内容，供后续分析使用。

## 前提条件

* 已生成 `output/jobs.json`
* 已生成 `output/scores.json`
* 高分岗位中存在 `security_id`
* CLI 已登录或 `boss detail` 可正常返回详情

## 用法

查看单个岗位详情：

```bash
boss detail <security_id>
```

如果提供批量脚本，可执行：

```bash
python boss-job-detail/scripts/fetch_details.py --min-score 60
```

## 工作流程

1. 读取 `output/scores.json`
2. 筛选高分岗位或用户指定岗位
3. 提取 `security_id`
4. 调用 `boss detail <security_id>`
5. 解析 CLI JSON 输出
6. 保存到 `output/details/`

## 输出格式

```json
{
  "job_id": "",
  "security_id": "",
  "title": "",
  "company": "",
  "salary": "",
  "city": "",
  "experience": "",
  "education": "",
  "description": "",
  "requirements": "",
  "skills": [],
  "welfare": [],
  "raw": {}
}
```

## 获取策略

| 场景        | 处理方式      |
| --------- | --------- |
| A 级岗位     | 优先获取详情    |
| B 级岗位     | 按用户需要获取详情 |
| C / D 级岗位 | 默认不获取详情   |
| 用户指定岗位    | 直接获取详情    |

## 技术要点

* 优先使用 `security_id`
* 不依赖 `boss show <index>` 作为长期引用
* 原始响应应保留，便于排查 CLI 输出变化
* 不对大量岗位进行无意义详情抓取

## 不做的步骤

| 步骤    | 原因                  |
| ----- | ------------------- |
| 自动投递  | 必须由用户在官网手动完成        |
| 自动打招呼 | 必须由用户在官网手动完成        |
| 简历生成  | 交给 `resume-tailor`  |
| 面试准备  | 交给 `interview-prep` |
| 报告生成  | 交给 `html-report`    |
