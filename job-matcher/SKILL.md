---

name: job-matcher
description: |
根据求职画像和岗位搜索结果进行岗位初筛评分，输出岗位推荐等级、推荐理由和风险提示。

本 Skill 是 boss-geek-auto 编排流程的子步骤（Step 2），通常在 boss-geek-auto 工作流中调用，不应作为入口 Skill 直接加载。
type: workflow
--------------

# 岗位匹配评分

读取 `geek-profile/profile.yaml` 和 `output/jobs.json`，由 Agent 按规则进行岗位评分，并生成 `output/scores.json`。

本 Skill 不依赖独立评分脚本。评分逻辑由 Agent 根据本文件中的规则执行。

## 前提条件

* 已生成 `output/jobs.json`
* 已配置 `geek-profile/profile.yaml`
* Agent 具备读取和写入本地文件的能力

## 输入文件

| 文件                          | 用途                    |
| --------------------------- | --------------------- |
| `geek-profile/profile.yaml` | 求职方向、城市、岗位偏好、风险词和评分配置 |
| `output/jobs.json`          | 岗位搜索结果                |

## 输出文件

```text
output/scores.json
```

## 工作流程

1. 读取 `geek-profile/profile.yaml`
2. 读取 `output/jobs.json`
3. 分析每个岗位的标题、公司、薪资、经验、学历、城市、技能、福利和原始文本
4. 根据评分维度给出匹配分
5. 标记岗位推荐等级
6. 写出推荐理由和风险提示
7. 保存为 `output/scores.json`

## 评分维度

| 维度   | 说明                                     |
| ---- | -------------------------------------- |
| 岗位方向 | 岗位名称或描述是否命中 `profile.yaml` 中的目标方向      |
| 技能匹配 | 是否命中 `profile.yaml` 中的目标技能、能力关键词或偏好关键词 |
| 经验要求 | 岗位经验、学历、身份要求是否匹配用户当前阶段                 |
| 城市匹配 | 是否符合 `profile.yaml` 中的目标城市、地区或远程要求     |
| 薪资   | 是否符合用户最低薪资或补贴要求；仅作为参考项，不作为唯一筛选标准       |
| 福利   | 是否命中用户偏好的福利、工作制度或组织条件                  |
| 风险词  | 是否命中 `profile.yaml` 中的规避词、风险词或不接受条件    |
| 学习价值 | 是否符合用户在 `profile.yaml` 中定义的成长目标或优先级    |

如果 `profile.yaml` 提供 `scoring_weights`，Agent 应优先使用用户配置的权重。示例结构如下：

```yaml
scoring_weights:
  target_roles: 30
  prefer: 20
  priority: 20
  target_city: 10
  current_stage: 10
  salary_min: 5
  avoid: 30
```

说明：

* 加分项和扣分项可以分别计算。
* `avoid` 通常作为扣分项，不要求与其他加分项总和为 100。
* 如果用户未配置权重，Agent 应根据匹配强弱进行合理评分，并保持解释透明。

## 推荐等级

| 等级 |   分数范围 | 含义     |
| -- | -----: | ------ |
| A  | 80-100 | 优先查看详情 |
| B  |  65-79 | 可以备选   |
| C  |  50-64 | 谨慎考虑   |
| D  |   0-49 | 跳过     |

## 推荐评分参考

| 情况                   | 建议处理           |
| -------------------- | -------------- |
| 明确命中目标岗位方向           | 加分             |
| 明确符合用户当前阶段           | 加分             |
| 描述中包含用户偏好的技能、能力或工作内容 | 加分             |
| 符合用户当前优先级            | 加分             |
| 薪资较低但学习价值明确          | 不明显扣分          |
| 信息不足但方向接近            | 保守评分，并写入 notes |
| 命中用户规避项              | 扣分             |
| 命中严重风险项              | 直接降级处理         |
| 与目标方向明显无关            | 降级处理           |

## 输出格式

```json
{
  "generated_at": "2026-01-01 12:00:00",
  "source": "agent",
  "job_count": 15,
  "scores": [
    {
      "index": 1,
      "job_id": "",
      "security_id": "",
      "title": "",
      "company": "",
      "salary": "",
      "city": "",
      "score": 82,
      "level": "A",
      "reasons": [
        "岗位名称命中目标方向",
        "岗位描述包含目标技能关键词",
        "经验要求适合用户当前阶段"
      ],
      "risks": [],
      "notes": [],
      "next_action": "建议查看岗位详情"
    }
  ]
}
```

## 输出要求

* 必须生成合法 JSON
* 必须覆盖写入 `output/scores.json`
* 必须只基于当前最新的 `output/jobs.json` 评分
* 必须保留岗位 `index`
* 必须保留 `job_id`
* 必须保留 `security_id`
* 必须给出 `score`
* 必须给出 `level`
* 必须给出推荐理由 `reasons`
* 如果存在风险，必须写入 `risks`
* 如果信息不足，建议写入 `notes`
* 必须给出 `next_action`
* 不确定时应保守评分，不要强行推荐

## 数据覆盖规则

* `output/scores.json` 始终表示最新一次岗位搜索结果对应的评分
* 每次评分都覆盖旧的 `output/scores.json`
* 不读取历史岗位文件
* 不合并历史评分结果

## 不做的步骤

| 步骤         | 原因                   |
| ---------- | -------------------- |
| 搜索岗位       | 交给 `boss-job-search` |
| 调用评分脚本     | 本 Skill 由 Agent 直接评分 |
| 获取 JD 详情   | 交给 `boss-job-detail` |
| 生成简历建议     | 交给 `resume-tailor`   |
| 生成面试材料     | 交给 `interview-prep`  |
| 生成 HTML 报告 | 交给 `html-report`     |
| 自动投递       | 必须由用户在官网手动完成         |
