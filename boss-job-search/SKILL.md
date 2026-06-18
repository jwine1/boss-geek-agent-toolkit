---
name: boss-job-search
description: |
  调用 boss-agent-cli 搜索 BOSS 直聘岗位，并将最新一次搜索结果标准化保存为本地 JSON。

  本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 1），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
---

# BOSS 直聘岗位搜索

通过 `boss search` 搜索岗位，解析 CLI 返回的 JSON 数据，生成统一格式的 `output/jobs.json`，供后续岗位评分、JD 分析和报告生成使用。

本 Skill 默认只保留最新一次搜索结果，不按关键词、城市或页数生成多个长期 JSON 文件。

## 前提条件

- 已安装 `boss-agent-cli`
- CLI 已登录或 `boss search` 可正常返回岗位
- 当前项目虚拟环境可运行 Python
- 已存在 `boss-job-search/scripts/run_search.py`

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
2. 清理上一轮搜索产生的派生文件，避免后续 Agent 读取过期数据
3. 调用 `boss search <query> --city <city>`
4. 保存最新原始 stdout/stderr 到 `output/raw/latest_p*.txt`
5. 优先解析 CLI JSON 输出
6. 提取并标准化岗位字段
7. 覆盖输出 `output/jobs.json`

## 固定输出文件

| 文件 | 说明 |
|---|---|
| `output/jobs.json` | 最新一次岗位搜索结果，每次运行覆盖 |
| `output/raw/latest_p*.txt` | 最新一次搜索的原始输出，每次运行覆盖 |

## 自动清理文件

每次执行岗位搜索时，脚本会清理上一轮派生数据：

```text
output/scores.json
output/asset_matches.json
output/report.html
output/details/
output/tailored_resumes/
output/interview/
```

清理原因：岗位数据时效性较低，若保留旧评分、旧详情或旧报告，Agent 可能混用不同搜索任务的数据。

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

- `stdout` 优先按 JSON 解析
- 如果 stdout 前后混入提示文本，从第一个 `{` 到最后一个 `}` 截取
- `security_id` 必须保留，供 `boss-job-detail` 使用
- `show_command` 只适合查看最近一次搜索结果
- `detail_command` 更适合稳定获取 JD
- 不生成 `jobs_<query>_<city>.json` 这类历史文件

## 不做的步骤

| 步骤 | 原因 |
|---|---|
| 自动投递 | 必须由用户在官网手动完成 |
| 自动打招呼 | 必须由用户在官网手动完成 |
| 岗位评分 | 交给 `job-matcher` |
| JD 详情分析 | 交给 `boss-job-detail` |
| 简历修改建议 | 交给 `resume-tailor` |
| HTML 报告生成 | 交给 `html-report` |
