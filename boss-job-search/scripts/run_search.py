# scripts/run_search.py
# 用途：调用 boss-agent-cli 搜索岗位，并兼容 JSON 输出 / 表格输出，生成 output/jobs.json

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def decode_bytes(data: bytes) -> str:
    for enc in ("utf-8", "gbk", "cp936"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)


def safe_name(text: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", text).strip("_")


def find_boss_cmd(user_value: str | None) -> str:
    if user_value:
        path = Path(os.path.expandvars(user_value)).expanduser()
        if path.exists():
            return str(path)

        found = shutil.which(user_value)
        if found:
            return found

        raise FileNotFoundError(f"你指定的 boss 命令不存在：{user_value}")

    for name in ("boss", "boss.exe"):
        found = shutil.which(name)
        if found:
            return found

    candidates = [
        Path.home() / ".local" / "bin" / "boss.exe",
        Path("E:/boss-geek-agent-toolkit/.venv/Scripts/boss.exe"),
        Path("E:/boss-agent/.venv/Scripts/boss.exe"),
    ]

    for p in candidates:
        if p.exists():
            return str(p)

    raise FileNotFoundError(
        "找不到 boss 命令。请使用 --boss-cmd 手动指定，例如："
        '--boss-cmd "C:\\Users\\j\\.local\\bin\\boss.exe"'
    )


def run_boss_search(boss_cmd: str, query: str, city: str, page: int) -> tuple[int, str, str]:
    cmd = [boss_cmd, "search", query, "--city", city]

    if page > 1:
        cmd += ["--page", str(page)]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        shell=False,
    )

    stdout = decode_bytes(result.stdout)
    stderr = decode_bytes(result.stderr)
    return result.returncode, stdout, stderr


def extract_json_text(raw_text: str) -> str | None:
    """
    boss search 有时会输出纯 JSON，有时前后可能混入提示文本。
    这里从第一个 { 到最后一个 } 截取 JSON。
    """
    text = raw_text.strip()
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    return text[start:end + 1]


def normalize_json_job(item: dict, page: int, index: int) -> dict:
    welfare = item.get("welfare") or []
    skills = item.get("skills") or []

    if not isinstance(welfare, list):
        welfare = [str(welfare)]

    if not isinstance(skills, list):
        skills = [str(skills)]

    title = item.get("title", "")
    company = item.get("company", "")
    salary = item.get("salary", "")
    city = item.get("city", "")
    district = item.get("district", "")
    exp = item.get("experience", "")
    edu = item.get("education", "")
    industry = item.get("industry", "")
    scale = item.get("scale", "")
    stage = item.get("stage", "")

    raw_parts = [
        title,
        company,
        salary,
        city,
        district,
        exp,
        edu,
        industry,
        scale,
        stage,
        " ".join(skills),
        " ".join(welfare),
    ]

    security_id = item.get("security_id", "")
    job_id = item.get("job_id", "")

    return {
        "page": page,
        "index": index,
        "job_id": job_id,
        "security_id": security_id,
        "title": title,
        "company": company,
        "salary": salary,
        "exp": exp,
        "edu": edu,
        "city": city,
        "district": district,
        "skills": skills,
        "welfare": welfare,
        "industry": industry,
        "scale": scale,
        "stage": stage,
        "boss_name": item.get("boss_name", ""),
        "boss_title": item.get("boss_title", ""),
        "boss_active": item.get("boss_active", ""),
        "greeted": item.get("greeted", False),
        "raw_text": " | ".join([str(x) for x in raw_parts if x]),
        "show_command": f"boss show {index}",
        "detail_command": f"boss detail {security_id}" if security_id else "",
    }


def parse_json_output(raw_text: str, page: int) -> tuple[list[dict], dict | None]:
    json_text = extract_json_text(raw_text)
    if not json_text:
        return [], None

    try:
        obj = json.loads(json_text)
    except json.JSONDecodeError:
        return [], None

    if not isinstance(obj, dict):
        return [], obj

    if obj.get("ok") is not True:
        return [], obj

    data = obj.get("data", [])
    if not isinstance(data, list):
        return [], obj

    jobs = []
    for i, item in enumerate(data, start=1):
        if isinstance(item, dict):
            jobs.append(normalize_json_job(item, page, i))

    return jobs, obj


def parse_table_output(raw_text: str, page: int) -> list[dict]:
    """
    兜底：兼容旧版 Rich 表格输出。
    """
    text = strip_ansi(raw_text)
    jobs = []

    for line in text.splitlines():
        if "│" not in line:
            continue

        parts = [p.strip() for p in line.split("│")]
        if len(parts) < 9:
            continue

        cols = parts[1:-1]
        if len(cols) < 7:
            continue

        index_text = cols[0]

        if index_text.isdigit():
            job = {
                "page": page,
                "index": int(index_text),
                "job_id": "",
                "security_id": "",
                "title": cols[1],
                "company": cols[2],
                "salary": cols[3],
                "exp": cols[4],
                "edu": cols[5],
                "city": cols[6],
                "district": "",
                "skills": [],
                "welfare": [],
                "industry": "",
                "scale": "",
                "stage": "",
                "boss_name": "",
                "boss_title": "",
                "boss_active": "",
                "greeted": False,
                "raw_text": " | ".join(cols[1:]),
                "show_command": f"boss show {index_text}",
                "detail_command": "",
            }
            jobs.append(job)

        elif jobs and index_text == "":
            keys = ["index", "title", "company", "salary", "exp", "edu", "city"]
            for i, key in enumerate(keys[1:], start=1):
                if i < len(cols) and cols[i]:
                    jobs[-1][key] = (jobs[-1][key] + " " + cols[i]).strip()

            jobs[-1]["raw_text"] = " | ".join(
                [
                    jobs[-1].get("title", ""),
                    jobs[-1].get("company", ""),
                    jobs[-1].get("salary", ""),
                    jobs[-1].get("exp", ""),
                    jobs[-1].get("edu", ""),
                    jobs[-1].get("city", ""),
                ]
            )

    return jobs


def parse_search_output(raw_text: str, page: int) -> tuple[list[dict], dict | None, str]:
    json_jobs, json_obj = parse_json_output(raw_text, page)
    if json_jobs:
        return json_jobs, json_obj, "json"

    table_jobs = parse_table_output(raw_text, page)
    return table_jobs, json_obj, "table"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="搜索关键词，例如：Java / 中台管培生")
    parser.add_argument("--city", default="南京", help="城市，例如：南京")
    parser.add_argument("--pages", type=int, default=1, help="搜索页数")
    parser.add_argument("--boss-cmd", default=None, help="boss.exe 路径；不填则自动寻找")
    parser.add_argument("--out", default="output/jobs.json", help="输出 jobs.json 路径")
    args = parser.parse_args()

    boss_cmd = find_boss_cmd(args.boss_cmd)
    print(f"使用 boss 命令：{boss_cmd}")

    output_dir = Path("output")
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    all_jobs = []
    all_errors = []
    source_objects = []

    for page in range(1, args.pages + 1):
        code, stdout, stderr = run_boss_search(boss_cmd, args.query, args.city, page)

        raw_file = raw_dir / f"search_raw_{safe_name(args.query)}_{safe_name(args.city)}_p{page}.txt"
        raw_file.write_text(stdout + "\n\n[stderr]\n" + stderr, encoding="utf-8")

        if code != 0:
            all_errors.append(
                {
                    "page": page,
                    "returncode": code,
                    "stderr": stderr,
                    "raw_file": str(raw_file),
                }
            )
            continue

        jobs, source_obj, mode = parse_search_output(stdout, page)

        if source_obj is not None:
            source_objects.append(
                {
                    "page": page,
                    "pagination": source_obj.get("pagination") if isinstance(source_obj, dict) else None,
                    "hints": source_obj.get("hints") if isinstance(source_obj, dict) else None,
                }
            )

        print(f"第 {page} 页解析模式：{mode}，岗位数：{len(jobs)}")
        all_jobs.extend(jobs)

    data = {
        "query": args.query,
        "city": args.city,
        "pages": args.pages,
        "boss_cmd": boss_cmd,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "job_count": len(all_jobs),
        "jobs": all_jobs,
        "source": source_objects,
        "errors": all_errors,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"完成：共解析 {len(all_jobs)} 个岗位")
    print(f"输出文件：{out_path}")

    if len(all_jobs) == 0:
        print("警告：没有解析到岗位。请查看 output/raw/ 下的原始输出文件。")

    if all_errors:
        print("存在搜索错误，请查看 output/raw/ 下的原始日志。")


if __name__ == "__main__":
    main()