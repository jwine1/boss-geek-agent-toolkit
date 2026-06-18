# boss-job-detail/scripts/run_detail.py
# 用途：UTF-8 安全地调用 boss detail，并将岗位详情保存到 output/details/
# 说明：本脚本只做 CLI 编码适配和落盘，不做岗位评分、不做简历建议、不自动投递。

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


def safe_name(text: str, max_len: int = 40) -> str:
    text = re.sub(r'[\\/:*?"<>|\s]+', "_", str(text)).strip("_")
    return text[:max_len] if text else "unknown"


def find_boss_cmd(user_value: str | None) -> str:
    if user_value:
        path = Path(os.path.expandvars(user_value)).expanduser()
        if path.exists():
            return str(path)

        found = shutil.which(user_value)
        if found:
            return found

        raise FileNotFoundError(f"你指定的 boss 命令不存在：{user_value}")

    candidates = [
        Path("E:/boss-geek-agent-toolkit/.venv/Scripts/boss.exe"),
        Path(".venv/Scripts/boss.exe"),
        Path(".venv/bin/boss"),
    ]

    for p in candidates:
        if p.exists():
            return str(p)

    for name in ("boss", "boss.exe"):
        found = shutil.which(name)
        if found:
            return found

    raise FileNotFoundError("找不到 boss 命令，请使用 --boss-cmd 指定 boss.exe 路径")


def extract_json_text(raw_text: str) -> str | None:
    text = raw_text.strip()
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    return text[start:end + 1]


def try_parse_json(raw_text: str):
    json_text = extract_json_text(raw_text)
    if not json_text:
        return None

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None


def run_detail(boss_cmd: str, security_id: str) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONLEGACYWINDOWSSTDIO"] = "0"

    result = subprocess.run(
        [boss_cmd, "detail", security_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        shell=False,
    )

    stdout = decode_bytes(result.stdout)
    stderr = decode_bytes(result.stderr)
    return result.returncode, stdout, stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--security-id", required=True, help="岗位 security_id")
    parser.add_argument("--index", default="000", help="岗位序号")
    parser.add_argument("--title", default="", help="岗位名称，用于文件名")
    parser.add_argument("--company", default="", help="公司名称，用于文件名")
    parser.add_argument("--boss-cmd", default=None, help="boss.exe 路径")
    parser.add_argument("--out-dir", default="output/details", help="详情输出目录")
    args = parser.parse_args()

    boss_cmd = find_boss_cmd(args.boss_cmd)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index_text = str(args.index).zfill(3)
    file_stem = f"{index_text}_{safe_name(args.company)}_{safe_name(args.title)}"
    raw_path = out_dir / f"{file_stem}.txt"
    json_path = out_dir / f"{file_stem}.json"

    code, stdout, stderr = run_detail(boss_cmd, args.security_id)

    raw_content = stdout + "\n\n[stderr]\n" + stderr
    raw_path.write_text(raw_content, encoding="utf-8")

    parsed = try_parse_json(stdout)

    data = {
        "index": args.index,
        "title": args.title,
        "company": args.company,
        "security_id": args.security_id,
        "boss_cmd": boss_cmd,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ok": code == 0,
        "returncode": code,
        "source": "boss detail",
        "raw_file": str(raw_path),
        "parsed": parsed,
        "stdout": stdout,
        "stderr": stderr,
    }

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": code == 0,
                "returncode": code,
                "json_file": str(json_path),
                "raw_file": str(raw_path),
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()