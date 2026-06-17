# scripts/generate_report.py
# 用途：根据 scores.json 生成求职岗位分析 HTML 报告

import argparse
import html
import json
from datetime import datetime
from pathlib import Path


def esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def level_class(level: str) -> str:
    if level == "强烈推荐":
        return "strong"
    if level == "推荐":
        return "good"
    if level == "可观望":
        return "watch"
    return "bad"


def make_reason_list(items: list[str]) -> str:
    if not items:
        return "<span class='muted'>无</span>"
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def generate_html(data: dict) -> str:
    results = data.get("results", [])
    query = data.get("query", "")
    city = data.get("city", "")
    job_count = data.get("job_count", len(results))

    strong_count = sum(1 for r in results if r.get("level") == "强烈推荐")
    good_count = sum(1 for r in results if r.get("level") == "推荐")
    watch_count = sum(1 for r in results if r.get("level") == "可观望")
    bad_count = sum(1 for r in results if r.get("level") == "不优先")

    top_rows = []
    for rank, item in enumerate(results, start=1):
        cls = level_class(item.get("level", ""))
        top_rows.append(
            f"""
            <tr>
                <td>{rank}</td>
                <td>{esc(item.get("title"))}</td>
                <td>{esc(item.get("company"))}</td>
                <td>{esc(item.get("salary"))}</td>
                <td>{esc(item.get("exp"))}</td>
                <td>{esc(item.get("edu"))}</td>
                <td>{esc(item.get("city"))}</td>
                <td><span class="score {cls}">{esc(item.get("score"))}</span></td>
                <td><span class="badge {cls}">{esc(item.get("level"))}</span></td>
                <td><code>{esc(item.get("show_command"))}</code></td>
            </tr>
            """
        )

    detail_cards = []
    for rank, item in enumerate(results, start=1):
        cls = level_class(item.get("level", ""))
        detail_cards.append(
            f"""
            <section class="card">
                <div class="card-title">
                    <span>#{rank} {esc(item.get("title"))}</span>
                    <span class="badge {cls}">{esc(item.get("level"))} · {esc(item.get("score"))}分</span>
                </div>
                <div class="meta">
                    {esc(item.get("company"))} ｜ {esc(item.get("salary"))} ｜ {esc(item.get("exp"))} ｜ {esc(item.get("edu"))} ｜ {esc(item.get("city"))}
                </div>
                <div class="two-col">
                    <div>
                        <h4>推荐理由</h4>
                        {make_reason_list(item.get("reasons", []))}
                    </div>
                    <div>
                        <h4>风险提示</h4>
                        {make_reason_list(item.get("risks", []))}
                    </div>
                </div>
                <p class="cmd">查看详情命令：<code>{esc(item.get("show_command"))}</code></p>
            </section>
            """
        )

    html_text = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>BOSS 求职岗位分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
            margin: 0;
            background: #f5f7fb;
            color: #1f2937;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px;
        }}
        h1 {{
            margin-bottom: 8px;
        }}
        .subtitle {{
            color: #6b7280;
            margin-bottom: 24px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }}
        .summary-card {{
            background: white;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .summary-card .num {{
            font-size: 28px;
            font-weight: 700;
            margin-top: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 32px;
        }}
        th, td {{
            padding: 12px 10px;
            border-bottom: 1px solid #e5e7eb;
            text-align: left;
            font-size: 14px;
            vertical-align: top;
        }}
        th {{
            background: #111827;
            color: white;
        }}
        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .score {{
            display: inline-block;
            min-width: 36px;
            text-align: center;
            padding: 4px 8px;
            border-radius: 999px;
            color: white;
            font-weight: 700;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            color: white;
            font-size: 13px;
        }}
        .strong {{
            background: #0f766e;
        }}
        .good {{
            background: #2563eb;
        }}
        .watch {{
            background: #d97706;
        }}
        .bad {{
            background: #6b7280;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .card-title {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: center;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .meta {{
            color: #6b7280;
            margin-bottom: 16px;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        h4 {{
            margin: 0 0 8px 0;
        }}
        ul {{
            margin-top: 6px;
            padding-left: 20px;
        }}
        .muted {{
            color: #9ca3af;
        }}
        .cmd {{
            margin-top: 12px;
            color: #4b5563;
        }}
        .note {{
            background: #fff7ed;
            border-left: 4px solid #f97316;
            padding: 14px 16px;
            border-radius: 8px;
            margin-bottom: 24px;
            color: #7c2d12;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>BOSS 求职岗位分析报告</h1>
    <div class="subtitle">
        关键词：{esc(query)} ｜ 城市：{esc(city)} ｜ 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>

    <div class="note">
        本报告基于 boss search 搜索列表进行第一轮粗筛。由于搜索列表不包含完整 JD，最终投递前应继续执行 <code>boss show 编号</code> 查看岗位详情。
    </div>

    <div class="summary">
        <div class="summary-card">
            <div>岗位总数</div>
            <div class="num">{job_count}</div>
        </div>
        <div class="summary-card">
            <div>强烈推荐</div>
            <div class="num">{strong_count}</div>
        </div>
        <div class="summary-card">
            <div>推荐</div>
            <div class="num">{good_count}</div>
        </div>
        <div class="summary-card">
            <div>可观望</div>
            <div class="num">{watch_count}</div>
        </div>
        <div class="summary-card">
            <div>不优先</div>
            <div class="num">{bad_count}</div>
        </div>
    </div>

    <h2>岗位排序表</h2>
    <table>
        <thead>
            <tr>
                <th>排名</th>
                <th>岗位</th>
                <th>公司</th>
                <th>薪资</th>
                <th>经验</th>
                <th>学历</th>
                <th>城市</th>
                <th>分数</th>
                <th>等级</th>
                <th>详情命令</th>
            </tr>
        </thead>
        <tbody>
            {''.join(top_rows)}
        </tbody>
    </table>

    <h2>岗位详情分析</h2>
    {''.join(detail_cards)}
</div>
</body>
</html>
"""
    return html_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default="output/scores.json")
    parser.add_argument("--out", default="output/report.html")
    args = parser.parse_args()

    scores_path = Path(args.scores)
    if not scores_path.exists():
        raise FileNotFoundError(f"未找到评分文件：{scores_path}")

    data = json.loads(scores_path.read_text(encoding="utf-8"))
    html_text = generate_html(data)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_text, encoding="utf-8")

    print(f"报告已生成：{out_path.resolve()}")


if __name__ == "__main__":
    main()