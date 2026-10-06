import requests
from datetime import datetime, timezone, timedelta

URL = "https://mgeact.api.mgtv.com/activity/conf"
PARAMS = {
    "activity_sn": "top20250207xgylypx26m10",
    "uastr": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0",
    "origin": "mweb",
    "order_source": "8",
    "source": "search_recommend",
    "source_channel": "ecom",
    "osType": "h5",
    "did": "86f8dfdc-9e66-4100-a531-838a06d4e1a0",
    "uuid": "8819f78989635f9db365c9d8751f1646",
    "ticket": "C42E14B8F825311F988373C5F8880F5A",
    "xmtkt": "8940f8e30b20c0e9344512f5e68b0230",
    "smVersion": "1.0.0"
}
HEADERS = {"User-Agent": PARAMS["uastr"], "Referer": "https://h5.ecom.mgtv.com/"}

def fetch():
    resp = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=15)
    data = resp.json()
    if data.get("code") != 200:
        raise Exception(f"接口异常：{data.get('msg')}")
    return sorted(data["data"]["top_list"], key=lambda x: x["top"])[:20]

def build_html(top_list):
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    cards = ""
    for item in top_list:
        rank = item.get("top", 0)
        name = item.get("show_name", "")
        icon = item.get("icon", "")
        if rank == 1: color = "#f7c948"
        elif rank == 2: color = "#c9d1e0"
        elif rank == 3: color = "#cd7f4a"
        else: color = "#7a8296"
        cards += f"""
        <div class="card">
            <img class="icon" src="{icon}" alt="">
            <div class="info">
                <div class="rank" style="color:{color}">#{rank}</div>
                <div class="name">{name}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>拾月人气园长排行榜</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0b0d13; color:#e8eaf0;
         font-family:"Microsoft YaHei","PingFang SC",sans-serif;
         padding:16px; max-width:900px; margin:0 auto; }}
  h1 {{ font-size:20px; color:#f7c948; margin-bottom:4px; }}
  .time {{ font-size:12px; color:#5a6274; margin-bottom:16px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
           gap:10px; }}
  .card {{ display:flex; align-items:center; background:#161a24;
           border:1px solid #242938; border-radius:10px; padding:10px; }}
  .icon {{ width:48px; height:48px; border-radius:8px; object-fit:cover;
           flex-shrink:0; }}
  .info {{ margin-left:12px; overflow:hidden; }}
  .rank {{ font-size:13px; font-weight:bold; }}
  .name {{ font-size:13px; color:#e8eaf0; white-space:nowrap;
           overflow:hidden; text-overflow:ellipsis; }}
</style>
</head>
<body>
  <h1>🏆 拾月人气园长排行榜 TOP20</h1>
  <div class="time">最后更新：{now}</div>
  <div class="grid">{cards}
  </div>
</body>
</html>"""

if __name__ == "__main__":
    top_list = fetch()
    html = build_html(top_list)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成 index.html，共 {len(top_list)} 条")
