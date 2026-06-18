# scripts/generate_report.py
# 用途：根据 scores.json（+ jobs.json + details/）生成求职岗位分析 HTML 报告

import argparse
import html as html_mod
import json
import re
from datetime import datetime
from pathlib import Path


def esc(value) -> str:
    if value is None:
        return ""
    return html_mod.escape(str(value))


def level_css(level: str) -> str:
    """A/B/C/D → CSS class A/B/C/D; also handles legacy Chinese labels."""
    if level in ("A", "B", "C", "D"):
        return level
    legacy = {"强烈推荐": "A", "推荐": "B", "可观望": "C", "不优先": "D"}
    return legacy.get(level, "D")


def level_label(level: str) -> str:
    labels = {"A": "优先投递", "B": "可以备选", "C": "谨慎考虑", "D": "跳过"}
    return labels.get(level, level)


def make_list(items: list[str]) -> str:
    if not items:
        return '<span class="muted">无</span>'
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def load_scores(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jobs(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_details(dir_path: Path) -> dict[str, dict]:
    """Return {security_id: parsed_detail} from JSON files in details dir."""
    details: dict[str, dict] = {}
    if not dir_path.exists():
        return details
    for f in sorted(dir_path.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            sid = d.get("security_id", "")
            if sid:
                details[sid] = d
        except (json.JSONDecodeError, KeyError):
            pass
    return details


def build_job_index(jobs_data: dict | None) -> dict[str, dict]:
    """Build {job_id: job} lookup from jobs.json."""
    if not jobs_data:
        return {}
    jobs = jobs_data.get("jobs", [])
    return {j.get("job_id", ""): j for j in jobs}


def get_scores(data: dict) -> list[dict]:
    """Extract score list, supporting both 'scores' and legacy 'results'."""
    return data.get("scores") or data.get("results", [])


def generate_html(
    data: dict,
    jobs_data: dict | None,
    jobs_index: dict[str, dict],
    details: dict[str, dict],
) -> str:
    scores = get_scores(data)
    # query/city may be in scores.json or jobs.json
    query = data.get("query") or (jobs_data or {}).get("query", "")
    city = data.get("city") or (jobs_data or {}).get("city", "")
    job_count = data.get("job_count", len(scores))
    scoring_method = data.get("scoring_method", "")
    weights = data.get("weights", {})

    # --- summary counts ---
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for s in scores:
        lv = s.get("level", "D")
        if lv in counts:
            counts[lv] += 1
        else:
            # legacy Chinese label
            css = level_css(lv)
            counts[css] = counts.get(css, 0) + 1

    # --- scoring method badge ---
    scoring_badge = ""
    if scoring_method:
        weight_parts = []
        if weights:
            weight_parts = [f"{k}={v}" for k, v in weights.items()]
        scoring_badge = f'<span class="method-badge">评分方法：{scoring_method}</span>'
        if weight_parts:
            scoring_badge += (
                f'<span class="method-badge">权重：{", ".join(weight_parts)}</span>'
            )

    # --- sorting table rows ---
    top_rows = []
    for rank, item in enumerate(scores, start=1):
        lv = item.get("level", "D")
        cls = level_css(lv)
        jid = item.get("job_id", "")
        job = jobs_index.get(jid, {})
        exp = job.get("exp") or item.get("exp", "")
        edu = job.get("edu") or item.get("edu", "")
        industry = job.get("industry") or item.get("industry", "")
        dim = "color:#9ca3af;" if lv == "D" else ""

        top_rows.append(
            f"""<tr>
                <td style="{dim}">{rank}</td>
                <td style="{dim}">{esc(item.get('title'))}</td>
                <td style="{dim}">{esc(item.get('company'))}</td>
                <td style="{dim}">{esc(item.get('salary'))}</td>
                <td style="{dim}">{esc(exp)}</td>
                <td style="{dim}">{esc(edu)}</td>
                <td style="{dim}">{esc(industry)}</td>
                <td><span class="badge {cls}">{esc(item.get('score'))}</span></td>
                <td><span class="badge {cls}">{esc(lv)}</span></td>
            </tr>"""
        )

    # --- detail cards ---
    detail_cards = []
    for rank, item in enumerate(scores, start=1):
        lv = item.get("level", "D")
        cls = level_css(lv)
        jid = item.get("job_id", "")
        sid = item.get("security_id", "")
        job = jobs_index.get(jid, {})
        exp = job.get("exp") or item.get("exp", "")
        edu = job.get("edu") or item.get("edu", "")
        industry = job.get("industry") or ""
        scale = job.get("scale") or ""
        stage = job.get("stage") or ""
        skills = job.get("skills") or []
        district = job.get("district") or item.get("city", "")

        # company subtitle
        company_parts = [item.get("company", "")]
        if industry:
            company_parts.append(industry)
        if stage:
            company_parts.append(stage)
        if scale:
            company_parts.append(scale)
        company_sub = " · ".join(p for p in company_parts if p)

        # skill tags
        skill_tags = "".join(
            f'<span class="skill-tag">{esc(s)}</span>' for s in skills[:8]
        )

        # JD from details
        jd_html = ""
        detail = details.get(sid)
        if detail:
            desc = ""
            parsed = detail.get("parsed")
            if parsed and isinstance(parsed, dict):
                data = parsed.get("data", {}) if isinstance(parsed.get("data"), dict) else {}
                desc = data.get("description") or parsed.get("description") or ""
            if not desc:
                # old-format detail: description at top level
                desc = detail.get("description") or ""
            if desc:
                jd_html = (
                    f'<div class="jd-block"><h4>岗位详情</h4>'
                    f"{esc(desc)}</div>"
                )

        # notes
        notes_html = ""
        notes = item.get("notes", [])
        if notes:
            notes_html = (
                '<div class="notes-block"><h4>备注</h4>'
                + make_list(notes)
                + "</div>"
            )

        # next action
        next_action = item.get("next_action", "")
        action_html = ""
        if next_action:
            action_html = (
                f'<div class="next-action">'
                f'<span class="action-label">建议：</span>{esc(next_action)}'
                f"</div>"
            )

        card_class = "card" if cls != "B" else "card B"
        detail_cards.append(
            f"""<div class="{card_class}">
            <div class="card-header">
                <div>
                    <h3>#{rank} {esc(item.get('title'))}
                        <span class="badge {cls}">{esc(lv)} · {esc(item.get('score'))}分</span>
                    </h3>
                    <div class="company">{esc(company_sub)}</div>
                </div>
            </div>
            <div class="card-meta">
                <span class="salary">{esc(item.get('salary'))}</span>
                <span>{esc(edu)}</span>
                <span>{esc(exp)}</span>
                <span>{esc(district)}</span>
                {skill_tags}
            </div>
            {jd_html}
            <div class="cols">
                <div class="reason"><h4>推荐理由</h4>{make_list(item.get('reasons', []))}</div>
                <div class="risk-item"><h4>风险提示</h4>{make_list(item.get('risks', []))}</div>
            </div>
            {notes_html}
            {action_html}
            </div>"""
        )

    # --- detail summary (count of fetched JDs) ---
    detail_count = len(details)
    detail_info = ""
    if detail_count:
        detail_info = (
            f'<div class="info">本次共嵌入 <strong>{detail_count} 个岗位的完整 JD</strong>，'
            f"数据来源：BOSS 直聘实际抓取。</div>"
        )

    # --- footer stats ---
    a_pct = round(counts["A"] / job_count * 100) if job_count else 0

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BOSS 求职岗位分析报告 — {esc(query)} · {esc(city)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
            background: #f0f2f5; color: #1f2937; line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px; }}
        .header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
            color: white; padding: 40px 32px; border-radius: 16px; margin-bottom: 28px;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .header .meta {{ opacity: 0.85; font-size: 14px; line-height: 1.8; }}
        .info {{
            background: #f0f9ff; border-left: 4px solid #0ea5e9;
            padding: 14px 16px; border-radius: 8px; margin-bottom: 20px;
            color: #075985; font-size: 14px;
        }}
        .method-badge {{
            display: inline-block; background: #dbeafe; color: #1e40af;
            padding: 2px 8px; border-radius: 4px; margin: 2px; font-size: 12px;
        }}

        .summary {{
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 28px;
        }}
        .s-card {{
            background: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
        }}
        .s-card .label {{ font-size: 13px; color: #6b7280; margin-bottom: 6px; }}
        .s-card .num {{ font-size: 32px; font-weight: 700; }}
        .s-card.a .num {{ color: #0f766e; }}
        .s-card.b .num {{ color: #2563eb; }}
        .s-card.c .num {{ color: #d97706; }}
        .s-card.d .num {{ color: #6b7280; }}

        .section-title {{
            font-size: 22px; font-weight: 700; margin: 36px 0 18px 0;
            padding-bottom: 8px; border-bottom: 3px solid #e5e7eb;
        }}

        table {{
            width: 100%; border-collapse: collapse; background: white;
            border-radius: 12px; overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 32px;
        }}
        th, td {{
            padding: 12px 10px; border-bottom: 1px solid #e5e7eb;
            text-align: left; font-size: 13px;
        }}
        th {{ background: #111827; color: white; font-weight: 600; }}
        tr:hover td {{ background: #f9fafb; }}

        .badge {{
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            color: white; font-size: 12px; font-weight: 700;
            min-width: 28px; text-align: center;
        }}
        .badge.A {{ background: #0f766e; }}
        .badge.B {{ background: #2563eb; }}
        .badge.C {{ background: #d97706; }}
        .badge.D {{ background: #9ca3af; }}

        .card {{
            background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 4px solid #0f766e;
        }}
        .card.B {{ border-left-color: #2563eb; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 10px; }}
        .card-header h3 {{ font-size: 18px; flex: 1; }}
        .card-header .company {{ color: #4b5563; font-size: 14px; }}
        .card-meta {{
            display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;
            font-size: 13px; color: #6b7280;
        }}
        .card-meta span {{ background: #f3f4f6; padding: 3px 10px; border-radius: 6px; }}
        .card-meta .salary {{ background: #ecfdf5; color: #065f46; font-weight: 600; }}
        .skill-tag {{
            display: inline-block; background: #dbeafe; color: #1e40af;
            padding: 2px 8px; border-radius: 4px; margin: 2px; font-size: 12px;
        }}

        .jd-block {{
            background: #f9fafb; border-radius: 8px; padding: 16px; margin-top: 12px;
            font-size: 13px; line-height: 1.8; white-space: pre-wrap;
            border: 1px solid #e5e7eb;
        }}
        .jd-block h4 {{ margin-bottom: 8px; color: #1f2937; font-size: 15px; }}

        .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 12px; }}
        @media (max-width: 768px) {{
            .cols {{ grid-template-columns: 1fr; }}
            .summary {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        .cols h4 {{ font-size: 14px; color: #374151; margin-bottom: 8px; }}
        .cols ul {{ padding-left: 20px; }}
        .cols li {{ margin-bottom: 4px; font-size: 14px; }}
        .reason li {{ color: #065f46; }}
        .risk-item li {{ color: #991b1b; }}

        .notes-block {{
            margin-top: 12px; background: #f0f9ff; border-radius: 8px; padding: 12px 16px;
        }}
        .notes-block h4 {{ font-size: 14px; color: #075985; margin-bottom: 4px; }}
        .notes-block li {{ color: #075985; font-size: 14px; }}

        .next-action {{
            margin-top: 12px; padding: 10px 14px; background: #ecfdf5;
            border-radius: 8px; font-size: 14px; color: #065f46;
        }}
        .action-label {{ font-weight: 600; }}

        .warn {{
            background: #fffbeb; border-left: 4px solid #f59e0b;
            padding: 14px 16px; border-radius: 8px; margin-bottom: 20px;
            color: #92400e; font-size: 14px;
        }}
        .muted {{ color: #9ca3af; }}
    </style>
</head>
<body>
<div class="container">

<div class="header">
    <h1>BOSS 求职岗位分析报告</h1>
    <div class="meta">
        搜索关键词：{esc(query)} ｜ 城市：{esc(city)}<br>
        岗位总数：{job_count} ｜ A级：{counts['A']} ｜ B级：{counts['B']} ｜ C级：{counts['C']} ｜ D级：{counts['D']}<br>
        生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        {f"<br>{scoring_badge}" if scoring_badge else ""}
    </div>
</div>

{detail_info}

<div class="summary">
    <div class="s-card"><div class="label">岗位总数</div><div class="num" style="color:#1f2937;">{job_count}</div></div>
    <div class="s-card a"><div class="label">A级 · 优先投递</div><div class="num">{counts['A']}</div></div>
    <div class="s-card b"><div class="label">B级 · 可备选</div><div class="num">{counts['B']}</div></div>
    <div class="s-card c"><div class="label">C级 · 谨慎</div><div class="num">{counts['C']}</div></div>
    <div class="s-card d"><div class="label">D级 · 跳过</div><div class="num">{counts['D']}</div></div>
</div>

<h2 class="section-title">全部岗位排序</h2>
<table>
    <thead><tr>
        <th>#</th><th>岗位名称</th><th>公司</th><th>薪资</th>
        <th>经验</th><th>学历</th><th>行业</th><th>分数</th><th>等级</th>
    </tr></thead>
    <tbody>
        {''.join(top_rows)}
    </tbody>
</table>

<h2 class="section-title">岗位详情分析</h2>
{''.join(detail_cards)}

<div class="warn" style="margin-top:24px;">
    <strong>重要提醒：</strong><br>
    1. 所有投递请回到 BOSS 直聘官网手动操作，本工具不自动投递<br>
    2. A级 ({counts['A']}个) 建议优先查看详情和投递<br>
    3. D级 ({counts['D']}个) 命中风险词或与目标方向明显无关，建议跳过<br>
    4. A级占比 {a_pct}%，整体匹配度{'高' if a_pct >= 30 else '中' if a_pct >= 15 else '需扩大搜索'}
</div>

</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="根据 scores.json 生成求职岗位分析 HTML 报告"
    )
    parser.add_argument(
        "--scores", default="output/scores.json", help="评分文件路径"
    )
    parser.add_argument(
        "--jobs", default="output/jobs.json", help="岗位搜索文件路径（可选，用于补充行业/规模等信息）"
    )
    parser.add_argument(
        "--details-dir", default="output/details", help="岗位详情目录（可选，用于嵌入 JD）"
    )
    parser.add_argument(
        "--out", default="output/report.html", help="输出 HTML 路径"
    )
    args = parser.parse_args()

    scores_path = Path(args.scores)
    if not scores_path.exists():
        raise FileNotFoundError(f"未找到评分文件：{scores_path}")

    data = load_scores(scores_path)
    jobs_data = load_jobs(Path(args.jobs))
    jobs_index = build_job_index(jobs_data)
    details = load_details(Path(args.details_dir))

    html_text = generate_html(data, jobs_data, jobs_index, details)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_text, encoding="utf-8")

    scores = get_scores(data)
    print(
        f"报告已生成：{out_path.resolve()}\n"
        f"  岗位总数：{len(scores)}\n"
        f"  嵌入 JD：{len(details)} 个"
    )


if __name__ == "__main__":
    main()
