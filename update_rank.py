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

def build_html():
    """生成一个自带抓取逻辑的 HTML，数据由浏览器直接请求接口"""
    import json
    params_js = json.dumps(PARAMS, ensure_ascii=False)

    return """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>拾月人气园长排行榜</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0b0d13; color:#e8eaf0;
         font-family:"Microsoft YaHei","PingFang SC",sans-serif;
         padding:16px; max-width:900px; margin:0 auto; }
  h1 { font-size:20px; color:#f7c948; margin-bottom:4px; }
  .bar { display:flex; justify-content:space-between; align-items:center;
         margin-bottom:16px; }
  .time { font-size:12px; color:#5a6274; }
  button { background:#1e2433; color:#9cb3ff; border:none;
           padding:6px 14px; border-radius:6px; font-size:13px;
           cursor:pointer; }
  button:active { background:#2a3148; }
  button:disabled { color:#5a6274; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
          gap:10px; }
  .card { display:flex; align-items:center; background:#161a24;
          border:1px solid #242938; border-radius:10px; padding:10px; }
  .icon { width:48px; height:48px; border-radius:8px; object-fit:cover;
          flex-shrink:0; }
  .info { margin-left:12px; overflow:hidden; }
  .rank { font-size:13px; font-weight:bold; }
  .name { font-size:13px; color:#e8eaf0; white-space:nowrap;
          overflow:hidden; text-overflow:ellipsis; }
  .msg { padding:20px; text-align:center; color:#5a6274; }
</style>
</head>
<body>
  <h1>🏆 拾月人气园长排行榜 TOP20</h1>
  <div class="bar">
    <div class="time" id="time">加载中...</div>
    <button id="btn" onclick="loadData()">🔄 刷新</button>
  </div>
  <div class="grid" id="grid">
    <div class="msg">正在获取数据...</div>
  </div>

<script>
const API = "https://mgeact.api.mgtv.com/activity/conf";
const PARAMS = __PARAMS__;

function beijingTime() {
  const d = new Date();
  const t = new Date(d.getTime() + (d.getTimezoneOffset() + 480) * 60000);
  const p = n => String(n).padStart(2, "0");
  return t.getFullYear() + "-" + p(t.getMonth()+1) + "-" + p(t.getDate())
       + " " + p(t.getHours()) + ":" + p(t.getMinutes()) + ":" + p(t.getSeconds());
}

function loadData() {
  const btn = document.getElementById("btn");
  const timeEl = document.getElementById("time");
  const grid = document.getElementById("grid");
  btn.disabled = true;
  btn.textContent = "刷新中...";
  timeEl.textContent = "正在获取数据...";

  const qs = new URLSearchParams(PARAMS).toString();
  fetch(API + "?" + qs)
    .then(r => r.json())
    .then(data => {
      if (data.code !== 200) throw new Error(data.msg || "接口异常");
      const list = data.data.top_list
        .sort((a, b) => a.top - b.top).slice(0, 20);
      let html = "";
      for (const item of list) {
        const rank = item.top;
        let color = "#7a8296";
        if (rank === 1) color = "#f7c948";
        else if (rank === 2) color = "#c9d1e0";
        else if (rank === 3) color = "#cd7f4a";
        html += `<div class="card">
          <img class="icon" src="${item.icon}" alt="">
          <div class="info">
            <div class="rank" style="color:${color}">#${rank}</div>
            <div class="name">${item.show_name}</div>
          </div>
        </div>`;
      }
      grid.innerHTML = html;
      timeEl.textContent = "最后更新：" + beijingTime();
      btn.disabled = false;
      btn.textContent = "🔄 刷新";
    })
    .catch(err => {
      timeEl.textContent = "更新失败：" + err.message;
      btn.disabled = false;
      btn.textContent = "🔄 重试";
    });
}

loadData();
// 页面开着时，每 5 分钟自动刷新一次
setInterval(loadData, 5 * 60 * 1000);
</script>
</body>
</html>""".replace("__PARAMS__", params_js)

if __name__ == "__main__":
    html = build_html()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("已生成自更新版 index.html")
