# -*- coding: utf-8 -*-
"""
一人公司工作台 - 每日基础知识生成
数据源：knowledge.json（AI 基础 + 计算机基础 知识库）
每日按日期轮换切片，输出 data.json / data.js
"""
import json
import time
from datetime import date

AI_DAILY = 15    # 每天展示的 AI 基础条数
CS_DAILY = 20    # 每天展示的计算机基础条数


def load_kb():
    with open("knowledge.json", encoding="utf-8") as f:
        return json.load(f)


def rotate(items, n, offset):
    """循环偏移后取前 n 条，保证每天内容滚动更新"""
    k = len(items)
    if k == 0:
        return []
    offset = offset % k
    rotated = items[offset:] + items[:offset]
    return rotated[:n]


def build_cards(items, source):
    out = []
    for it in items:
        out.append({
            "title": it.get("term", ""),
            "summary": it.get("explain", ""),
            "url": "",
            "source": source,
            "ts": 0,
        })
    return out


def main():
    kb = load_kb()
    offset = date.today().toordinal()

    ai_items = build_cards(rotate(kb.get("ai", []), AI_DAILY, offset), "AI 基础")
    cs_items = build_cards(rotate(kb.get("cs", []), CS_DAILY, offset), "计算机基础")

    result = {
        "updateTime": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updateTs": int(time.time()),
        "date": date.today().strftime("%Y-%m-%d"),
        "total": len(ai_items) + len(cs_items),
        "ai_news": ai_items,
        "tech_news": cs_items,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    js = "window.HOT_DATA = " + json.dumps(result, ensure_ascii=False) + ";"
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(js)

    print(f"完成：AI 基础 {len(ai_items)} 条，计算机基础 {len(cs_items)} 条")
    print(f"更新日期：{result['date']}（知识库轮换 offset={offset}）")
    print("已写入 data.json / data.js")


if __name__ == "__main__":
    main()
