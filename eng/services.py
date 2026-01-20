import csv
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_words(dict_name: str):
    """读取 data/{dict_name}.csv -> list[dict]"""
    path = DATA_DIR / f"{dict_name}.csv"
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def _load_json(filename: str, default):
    path = DATA_DIR / filename
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(filename: str, obj):
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_history():
    return _load_json("history.json", [])

def load_quiz_log():
    return _load_json("quiz_log.json", [])

def append_quiz_log(payload: dict):
    """写入一条测验记录到 quiz_log.json"""
    logs = load_quiz_log()
    payload = dict(payload)
    payload.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logs.append(payload)
    _save_json("quiz_log.json", logs)

def clear_quiz_log():
    _save_json("quiz_log.json", [])
