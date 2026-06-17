# scripts/score_jobs.py
# 用途：根据求职偏好 profile.yaml 对岗位进行规则打分

import argparse
import json
import re
from pathlib import Path


def parse_simple_yaml(path: Path) -> dict:
    """
    极简 YAML 解析器。
    支持：
    key: value
    key:
      - item1
      - item2
    """
    if not path.exists():
        return {}

    data = {}
    current_key = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("- ") and current_key:
            data.setdefault(current_key, [])
            data[current_key].append(line[2:].strip())
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key

            if value == "":
                data[key] = []
            else:
                if value.isdigit():
                    data[key] = int(value)
                else:
                    data[key] = value

    return data


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def parse_salary_k(salary: str) -> tuple[int | None, int | None]:
    """
    解析：
    8-10K
    14-28K·14薪
    6-11K
    """
    if not salary:
        return None, None

    m = re.search(r"(\d+)\s*-\s*(\d+)\s*K", salary, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = re.search(r"(\d+)\s*K", salary, re.IGNORECASE)
    if m:
        value = int(m.group(1))
        return value, value

    return None, None


def contains_any(text: str, words: list[str]) -> list[str]:
    hits = []
    for word in words:
        if word and word in text:
            hits.append(word)
    return hits


def score_one_job(job: dict, profile: dict, resume_text: str) -> dict:
    title = job.get("title", "")
    company = job.get("company", "")
    salary = job.get("salary", "")
    exp = job.get("exp", "")
    edu = job.get("edu", "")
    city = job.get("city", "")

    text = " ".join([title, company, salary, exp, edu, city, job.get("raw_text", "")])

    score = 35
    reasons = []
    risks = []

    target_role = str(profile.get("target_role", "")).strip()
    target_roles = as_list(profile.get("target_roles"))
    if target_role:
        target_roles.append(target_role)

    role_hits = contains_any(title, target_roles)
    if role_hits:
        score += 20
        reasons.append(f"岗位名称匹配目标方向：{', '.join(role_hits)}")
    elif target_roles:
        partial_hits = [r for r in target_roles if any(ch in title for ch in r)]
        if partial_hits:
            score += 8
            reasons.append("岗位名称与目标方向存在部分关联")
        else:
            risks.append("岗位名称与目标方向匹配度不明显")

    target_city = str(profile.get("target_city", "")).strip()
    if target_city and target_city in city:
        score += 10
        reasons.append(f"城市匹配：{target_city}")
    elif target_city:
        score -= 5
        risks.append(f"城市不匹配：目标 {target_city}，岗位 {city}")

    salary_min = profile.get("salary_min", 0)
    if isinstance(salary_min, int) and salary_min > 0:
        salary_min_k = salary_min / 1000
        low, high = parse_salary_k(salary)

        if low is not None and low >= salary_min_k:
            score += 10
            reasons.append(f"薪资下限满足预期：{salary}")
        elif high is not None and high >= salary_min_k:
            score += 5
            reasons.append(f"薪资上限可达预期：{salary}")
        elif high is not None:
            score -= 8
            risks.append(f"薪资可能低于预期：{salary}")

    if "经验不限" in exp:
        score += 15
        reasons.append("经验要求友好：经验不限")
    elif "1-3年" in exp:
        score += 8
        reasons.append("经验要求相对可接受：1-3年")
    elif "3-5年" in exp:
        score -= 5
        risks.append("经验要求偏高：3-5年")
    elif "5-10年" in exp or "10年" in exp:
        score -= 15
        risks.append(f"经验要求明显偏高：{exp}")

    if "本科" in edu:
        score += 8
        reasons.append("学历要求为本科，匹配常规校招/初中级岗位")
    elif "大专" in edu:
        score += 3
        reasons.append("学历门槛相对宽松")
    elif "硕士" in edu:
        score += 5
        reasons.append("学历要求较高，需要结合自身背景判断")

    must_have = as_list(profile.get("must_have"))
    for word in must_have:
        if word in text:
            score += 6
            reasons.append(f"满足硬偏好：{word}")
        else:
            # 搜索列表信息较少，不能重扣
            score -= 2
            risks.append(f"搜索列表未显示硬偏好：{word}")

    prefer = as_list(profile.get("prefer"))
    for word in prefer:
        if word in text:
            score += 4
            reasons.append(f"满足加分偏好：{word}")

    avoid = as_list(profile.get("avoid"))
    avoid_hits = contains_any(text, avoid)
    for word in avoid_hits:
        score -= 15
        risks.append(f"命中规避项：{word}")

    common_risk_words = ["外包", "派遣", "销售", "电销", "培训机构", "不缴纳", "大小周", "单休"]
    risk_hits = contains_any(text, common_risk_words)
    for word in risk_hits:
        score -= 12
        risks.append(f"岗位存在潜在风险词：{word}")

    # 简历关键词弱匹配：第一版只做很轻量加分
    if resume_text:
        resume_keywords = ["Java", "Python", "SQL", "项目", "实习", "管理", "沟通", "数据分析"]
        matched = [kw for kw in resume_keywords if kw in resume_text and kw in text]
        if matched:
            score += min(10, len(matched) * 2)
            reasons.append(f"岗位关键词与简历存在交集：{', '.join(matched)}")

    score = max(0, min(100, score))

    if score >= 80:
        level = "强烈推荐"
    elif score >= 65:
        level = "推荐"
    elif score >= 50:
        level = "可观望"
    else:
        level = "不优先"

    return {
        "page": job.get("page"),
        "index": job.get("index"),
        "title": title,
        "company": company,
        "salary": salary,
        "exp": exp,
        "edu": edu,
        "city": city,
        "score": score,
        "level": level,
        "reasons": reasons,
        "risks": risks,
        "show_command": job.get("show_command", ""),
        "raw_text": job.get("raw_text", ""),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", default="output/jobs.json")
    parser.add_argument("--profile", default="data/profile.yaml")
    parser.add_argument("--resume", default="data/resume_base.md")
    parser.add_argument("--out", default="output/scores.json")
    args = parser.parse_args()

    jobs_path = Path(args.jobs)
    profile_path = Path(args.profile)
    resume_path = Path(args.resume)

    if not jobs_path.exists():
        raise FileNotFoundError(f"未找到岗位文件：{jobs_path}")

    jobs_data = json.loads(jobs_path.read_text(encoding="utf-8"))
    profile = parse_simple_yaml(profile_path)
    resume_text = resume_path.read_text(encoding="utf-8") if resume_path.exists() else ""

    results = []
    for job in jobs_data.get("jobs", []):
        results.append(score_one_job(job, profile, resume_text))

    results.sort(key=lambda x: x["score"], reverse=True)

    output = {
        "query": jobs_data.get("query"),
        "city": jobs_data.get("city"),
        "job_count": len(results),
        "profile": profile,
        "results": results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"完成：共评分 {len(results)} 个岗位")
    print(f"输出文件：{out_path}")


if __name__ == "__main__":
    main()