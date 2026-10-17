# -*- coding: utf-8 -*-
"""
一人公司工作台 - 每日内容生成
混合策略：热榜（实时）+ 基础知识（每日轮换）
  热榜源：掘金（技术/AI 社区）、今日头条热榜、百度热搜（兜底）
  基础源：knowledge.json 按日期轮换
输出：data.json / data.js
"""
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

# GitHub Actions  runner 是 UTC，必须显式按北京时间算「今天」，否则 07:30 那次会标成前一天
CST = timezone(timedelta(hours=8))
def now_cst():
    return datetime.now(CST)
def today_cst():
    return now_cst().strftime("%Y-%m-%d")

# 每个模块：热榜条数 + 基础条数
HOT_N = 8
BASE_N = 7

AI_KEYS = ["ai", "人工智能", "大模型", "llm", "gpt", "agent", "智能体", "模型",
           "机器学习", "深度学习", "nlp", "aigc", "提示词", "prompt", "chatgpt",
           "claude", "deepseek", "qwen", "通义", "文心", "豆包", "kimi", "多模态",
           "transformer", "diffusion", "rag", "微调", "推理", "具身"]

TECH_KEYS = ["芯片", "半导体", "cpu", "gpu", "显卡", "手机", "电脑", "系统", "windows",
             "android", "ios", "linux", "鸿蒙", "华为", "小米", "苹果", "英伟达",
             "intel", "amd", "arm", "内存", "电池", "屏幕", "数码", "科技", "互联网",
             "开源", "代码", "编程", "开发者", "数据库", "云计算", "服务器", "网络",
             "安全", "漏洞", "机器人", "自动驾驶", "新能源", "软件", "硬件", "发布"]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_json(url, data=None, timeout=15):
    body = json.dumps(data).encode() if data else None
    h = dict(UA)
    if data:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h, method="POST" if data else "GET")
    r = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(r.read().decode("utf-8", "replace"))


def hit(text, keys):
    t = (text or "").lower()
    return any(k in t for k in keys)


def fetch_juejin(limit=40):
    """掘金推荐流（最新），返回文章列表"""
    d = get_json("https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed",
                 {"id_type": 2, "sort_type": 3, "cursor": "0", "limit": limit})
    out = []
    for it in d.get("data") or []:
        a = (it.get("item_info") or {}).get("article_info") or {}
        title = (a.get("title") or "").strip()
        if not title:
            continue
        out.append({
            "title": title,
            "summary": (a.get("brief_content") or "").strip()[:120],
            "url": "https://juejin.cn/post/" + str(a.get("article_id") or ""),
            "ts": int(a.get("ctime") or 0),
        })
    return out


def fetch_toutiao(limit=40):
    """今日头条热榜"""
    d = get_json("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc")
    out = []
    for it in (d.get("data") or [])[:limit]:
        title = (it.get("Title") or "").strip()
        if not title:
            continue
        cid = it.get("ClusterId")
        out.append({
            "title": title,
            "summary": (it.get("HotValue") and f"热度 {it.get('HotValue')}") or "",
            "url": it.get("Url") or f"https://www.toutiao.com/trending/{cid}/",
            "ts": int(time.time()),
        })
    return out


def fetch_baidu(limit=40):
    """百度热搜（兜底）"""
    d = get_json("https://top.baidu.com/api/board?platform=wise&tab=realtime")
    out = []
    for card in (d.get("data", {}).get("cards") or []):
        for it in card.get("content") or []:
            title = (it.get("word") or it.get("query") or "").strip()
            if not title:
                continue
            out.append({
                "title": title,
                "summary": (it.get("desc") or "")[:120],
                "url": it.get("url") or f"https://www.baidu.com/s?wd={urllib.parse.quote(title)}",
                "ts": int(time.time()),
            })
    return out[:limit]


def pick(items, keys, n, source):
    """按关键词挑前 n 条；不足则补无关条目"""
    hot = [x for x in items if hit(x["title"] + " " + x.get("summary", ""), keys)]
    rest = [x for x in items if x not in hot]
    sel = (hot + rest)[:n]
    for x in sel:
        x["source"] = source
    return sel


def load_kb():
    with open("knowledge.json", encoding="utf-8") as f:
        return json.load(f)


def rotate(items, n, offset):
    k = len(items)
    if k == 0:
        return []
    offset = offset % k
    return (items[offset:] + items[:offset])[:n]


def build_base(kb_items, n, offset, source):
    out = []
    for it in rotate(kb_items, n, offset):
        out.append({
            "title": it.get("term", ""),
            "summary": it.get("explain", ""),
            "url": "",
            "source": source,
            "ts": 0,
        })
    return out


def main():
    offset = now_cst().toordinal()
    logs = []

    # ---- 热榜 ----
    try:
        jj = fetch_juejin()
        logs.append(f"掘金 {len(jj)} 条")
    except Exception as e:
        jj = []
        logs.append(f"掘金失败 {e}")

    hot_general = []
    for name, fn in (("今日头条", fetch_toutiao), ("百度热搜", fetch_baidu)):
        try:
            hot_general = fn()
            if hot_general:
                logs.append(f"{name} {len(hot_general)} 条")
                break
        except Exception as e:
            logs.append(f"{name}失败 {e}")

    ai_hot = pick(jj, AI_KEYS, HOT_N, "掘金·AI热文") if jj else []
    tech_hot = pick(hot_general, TECH_KEYS, HOT_N, "今日热榜")

    # ---- 基础知识 ----
    kb = load_kb()
    ai_base = build_base(kb.get("ai", []), BASE_N, offset, "AI 基础")
    cs_base = build_base(kb.get("cs", []), BASE_N, offset * 7 + 3, "计算机基础")

    ai_news = ai_hot + ai_base
    tech_news = tech_hot + cs_base

    _now = now_cst()
    result = {
        "updateTime": _now.strftime("%Y-%m-%d %H:%M:%S"),
        "updateTs": int(time.time()),
        "date": _now.strftime("%Y-%m-%d"),
        "total": len(ai_news) + len(tech_news),
        "ai_news": ai_news,
        "tech_news": tech_news,
    }

    if result["total"] < 10:
        raise SystemExit("抓取异常：内容过少，保留旧数据")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.HOT_DATA = " + json.dumps(result, ensure_ascii=False) + ";")

    print(" | ".join(logs))
    print(f"AI：热榜 {len(ai_hot)} + 基础 {len(ai_base)}")
    print(f"计算机：热榜 {len(tech_hot)} + 基础 {len(cs_base)}")
    print(f"写入完成 · {result['updateTime']} · 共 {result['total']} 条")


if __name__ == "__main__":
    main()
