import csv
import math
import os
import random
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render

from .services import append_quiz_log, clear_quiz_log, load_quiz_log


DICT_LIST = [
    {"id": "cet4", "name": "CET-4"},
    {"id": "cet6", "name": "CET-6"},
    {"id": "考研英语", "name": "考研英语"},
]


def _data_dir() -> Path:
    return Path(settings.BASE_DIR) / "eng" / "data"


def _csv_path(dict_id: str) -> Path:
    return _data_dir() / f"{dict_id}.csv"


def _load_words_from_csv(dict_id: str):
    path = _csv_path(dict_id)
    if not path.exists():
        return [], str(path)

    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            w = (r.get("word") or "").strip()
            m = (r.get("meaning") or "").strip()
            p = (r.get("pos") or "").strip()
            if w and m:
                rows.append({"word": w, "meaning": m, "pos": p})
    return rows, str(path)


def cover(request):
    return render(request, "cover.html")


def home(request):
    data_status = {}
    for d in DICT_LIST:
        words, _ = _load_words_from_csv(d["id"])
        data_status[d["id"]] = len(words)

    return render(
        request,
        "index.html",
        {
            "dicts": DICT_LIST,
            "data_status": data_status,
            "history": None,
        },
    )


def learn(request):
    dict_id = request.GET.get("dict", "cet4").strip()
    if dict_id not in {d["id"] for d in DICT_LIST}:
        return HttpResponseBadRequest("Invalid dict")

    try:
        page = int(request.GET.get("page", "1"))
    except:
        page = 1
    page = max(1, page)

    try:
        size = int(request.GET.get("size", "18"))
    except:
        size = 18
    if size not in (18, 24, 36, 48):
        size = 18

    words_all, path = _load_words_from_csv(dict_id)
    if not words_all:
        return HttpResponse(f"CSV not found or empty: {path}", status=500)

    total_pages = max(1, math.ceil(len(words_all) / size))
    if page > total_pages:
        page = total_pages

    start = (page - 1) * size
    end = start + size
    words = words_all[start:end]

    return render(
        request,
        "learn.html",
        {
            "dict_name": dict_id,
            "words": words,
            "page": page,
            "size": size,
            "total_pages": total_pages,
        },
    )


def quiz_select(request):
    return render(request, "quiz_select.html", {"dicts": DICT_LIST})


def quiz(request):
    if request.method == "GET":
        dict_id = request.GET.get("dict", "cet4").strip()
        if dict_id not in {d["id"] for d in DICT_LIST}:
            return HttpResponseBadRequest("Invalid dict")

        try:
            size = int(request.GET.get("size", "10"))
        except:
            size = 10
        size = max(1, min(50, size))

        words, path = _load_words_from_csv(dict_id)
        if len(words) < 4:
            return HttpResponse(f"Not enough rows in: {path}", status=500)

        qcount = min(size, len(words))
        qs = random.sample(words, k=qcount)
        meanings_pool = [w["meaning"] for w in words if w["meaning"]]

        items = []
        for q in qs:
            right = q["meaning"]
            wrongs = list({m for m in meanings_pool if m != right})
            random.shuffle(wrongs)
            opts = [right] + wrongs[:3]
            random.shuffle(opts)
            items.append({"word": q["word"], "right": right, "options": opts})

        return render(
            request,
            "quiz.html",
            {
                "dict_name": dict_id,
                "size": size,
                "items": items,
            },
        )

    dict_id = request.POST.get("dict", "cet4").strip()
    try:
        qcount = int(request.POST.get("qcount", "0"))
    except:
        qcount = 0

    correct = 0
    total = max(0, qcount)

    for i in range(total):
        user_ans = request.POST.get(f"q{i}", "")
        right = request.POST.get(f"right{i}", "")
        if user_ans and right and user_ans == right:
            correct += 1

    score = int(correct / max(1, total) * 100)

    append_quiz_log(
        {
            "dict_name": dict_id,
            "total": total,
            "correct": correct,
            "score": score,
        }
    )

    return render(
        request,
        "quiz_result.html",
        {
            "dict": dict_id,
            "total": total,
            "correct": correct,
            "score": score,
        },
    )


def stats(request):
    logs = list(reversed(load_quiz_log()))
    return render(request, "stats.html", {"logs": logs})


def stats_clear(request):
    clear_quiz_log()
    return redirect("/stats/")