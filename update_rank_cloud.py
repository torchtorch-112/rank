# -*- coding: utf-8 -*-
"""
云端采集脚本（GitHub Actions 用）
- Cookie 从环境变量 WEIBO_COOKIE 读取
- 只输出 cloud_data.json（和可选的 cloud_vote_history.csv）
- 不会碰本地的 vote_history.csv
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

# ===============================
# 微博接口
# ===============================
URL = "https://dianshi.weibo.com/vote_rank"

PARAMS = {
    "c": "applet",
    "cid": "1420",
    "sign": "14cfc1b889947f1618c05b86bb4554564e65ac45",
    "ts": "1791735111",
    "current_uid": "7956906130",
    "tid": "2448",
    "page": "1",
    "pagesize": "15",
    "version": "2",
    "gsid": "_2A25Hz-RWDeRxGeFH7lQY8CjNyDyIHXVi3XCerDV6PUJbkdAbLXT_kWpNevvXP5hUyEBuUld9SPEfS3f5wlhgDrFn"
}

# Cookie 从 GitHub Secret 读取（环境变量名 WEIBO_COOKIE）
COOKIE = os.environ.get("WEIBO_COOKIE", "")

HEADERS = {
    "host": "dianshi.weibo.com",
    "accept-language": "zh-CN,zh;q=0.8",
    "referer": "https://wboxservice.com/l331zrkexk/546/page-frame.html",
    "user-agent": "Mozilla/5.0 (Linux; Android 15; 2206123SC Build/V417IR; wv) AppleWebKit/537.36 Chrome/110 Mobile Weibo",
    "wbox-app-language": "zh",
    "wb-lang": "zh_CN",
    "wbox-color-scheme": "light",
    "cookie": COOKIE
}

# ===============================
# 配置
# ===============================
TRACKED_NAMES = ["十个勤天", "苏新皓", "朱志鑫", "张泽禹"]
MAX_POINTS = 1080                 # 18 小时 × 60 分钟
JSON_FILE = "cloud_data.json"
CSV_FILE = "cloud_vote_history.csv"   # 云端备份用，不想存可以删掉相关代码

# 北京时间
BJ_TZ = timezone(timedelta(hours=8))


def now_bj():
    return datetime.now(BJ_TZ)


# ===============================
# 抓取
# ===============================
def get_vote():
    if not COOKIE:
        print("❌ 环境变量 WEIBO_COOKIE 为空，请检查 GitHub Secret")
        return None
    try:
        r = requests.get(URL, params=PARAMS, headers=HEADERS,
                         timeout=15,
                         proxies={"http": None, "https": None})
        data = r.json()
        if data.get("code") != 1000:
            print(f"接口异常 code={data.get('code')}  full={data}")
            return None

        result = {}
        for item in data["data"]["list"]:
            if item["name"] in TRACKED_NAMES:
                result[item["name"]] = int(item["by_vote_num"])

        missing = [n for n in TRACKED_NAMES if n not in result]
        if missing:
            print(f"⚠️ 本帧未返回: {missing}")
        return result

    except Exception as e:
        print(f"请求错误: {e}")
        return None


# ===============================
# 更新 JSON
# ===============================
def load_json():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"读取 {JSON_FILE} 失败: {e}，重新开始")
    return {"times": [], "series": {name: [] for name in TRACKED_NAMES}}


def save_json(history):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def update_json(ts_full, result):
    history = load_json()

    # 补全缺失的 key（比如以后加了新选手）
    for name in TRACKED_NAMES:
        history["series"].setdefault(name, [float("nan")] * len(history["times"]))

    history["times"].append(ts_full)

    for name in TRACKED_NAMES:
        history["series"][name].append(result.get(name, None))

    # 裁剪
    if len(history["times"]) > MAX_POINTS:
        history["times"] = history["times"][-MAX_POINTS:]
        for name in history["series"]:
            history["series"][name] = history["series"][name][-MAX_POINTS:]

    save_json(history)
    print(f"✅ 已写入 {JSON_FILE}，共 {len(history['times'])} 个时间点")


# ===============================
# 可选：追加 CSV 备份
# ===============================
def append_csv(ts_full, result):
    import csv
    is_new = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["时间", "选手", "票数"])
        for name, value in result.items():
            writer.writerow([ts_full, name, value])


# ===============================
# 主流程
# ===============================
def main():
    result = get_vote()
    if not result:
        print("本次无数据，跳过")
        return

    ts_full = now_bj().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts_full}] {result}")

    update_json(ts_full, result)
    append_csv(ts_full, result)   # 不想备份 CSV 就删这一行


if __name__ == "__main__":
    main()
