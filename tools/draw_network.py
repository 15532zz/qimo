# -*- coding: utf-8 -*-
"""捕获真实网络请求并渲染 Network 面板风格图"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

TOOLS = os.path.dirname(os.path.abspath(__file__))
FONT = "C:\\Windows\\Fonts\\msyh.ttc"

def font(size, bold=False):
    p = "C:\\Windows\\Fonts\\msyhbd.ttc" if bold else FONT
    return ImageFont.truetype(p, size)

reqs = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page()
    def on_resp(r):
        reqs.append({"url": r.url.replace("http://localhost:8080", ""),
                     "status": r.status, "type": r.headers.get("content-type", "").split(";")[0],
                     "size": 0})
    pg.on("response", on_resp)
    pg.on("requestfinished", lambda r: None)
    try:
        pg.goto("http://localhost:8080/test-error.html", wait_until="networkidle", timeout=30000)
    except Exception:
        pass
    pg.wait_for_timeout(2500)
    b.close()

# 计算传输大小：再请求一次取 body 长度（仅本站资源）
import urllib.request
for r in reqs:
    if r["url"].startswith("/") and r["status"] == 200:
        try:
            with urllib.request.urlopen("http://localhost:8080" + r["url"]) as resp:
                r["size"] = len(resp.read())
        except Exception:
            pass

with open(f"{TOOLS}/network-log.json", "w", encoding="utf-8") as f:
    json.dump(reqs, f, ensure_ascii=False, indent=2)

# 只保留关键请求（过滤 CDN 的部分噪音，保留 jquery/echarts/bootstrap与本站）
keep = [r for r in reqs if r["url"].startswith("/") or "jquery" in r["url"] or "echarts" in r["url"]]
keep = keep[:16]

# ===== 渲染 =====
LH, PAD, ROW = 42, 24, 42
W = 1560
H = 80 + ROW * len(keep) + PAD
img = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 52], fill="#f1f3f4")
d.text((PAD, 12), "DevTools - Network（网络请求记录 · 含 404 失败请求）", font=font(21, True), fill="#202124")

cols = [(PAD, 40, "状态"), (PAD+80, 470, "名称"), (PAD+560, 660, "类型"), (PAD+820, 900, "大小"), (PAD+1060, 1120, "时间"), (PAD+1200, 1560, "域名")]
hx = [(60, "Status"), (150, "Name"), (740, "Type"), (900, "Size"), (1080, "Time"), (1290, "Domain")]
# 表头
d.rectangle([0, 52, W, 52+ROW], fill="#f8f9fa")
for x, t in hx:
    d.text((x, 60), t, font=font(18, True), fill="#5f6368")
d.line([0, 52+ROW, W, 52+ROW], fill="#dadce0")

y = 52 + ROW
for i, r in enumerate(keep):
    if i % 2 == 1:
        d.rectangle([0, y, W, y+ROW-6], fill="#f8f9fa")
    status = r["status"]
    sc = "#188038" if status == 200 else ("#d93025" if status >= 400 else "#e37400")
    d.text((60, y+2), str(status), font=font(17), fill=sc)
    name = r["url"].split("?")[0][-38:]
    d.text((150, y+2), name, font=font(17), fill="#202124")
    ttype = {"application/json": "json", "text/html": "html", "text/css": "css",
             "application/javascript": "js", "image/png": "png",
             "font/bootstrap-icons": "font", "": "xhr"}.get(r["type"], r["type"][:14])
    d.text((740, y+2), ttype, font=font(17), fill="#5f6368")
    size = f"{r['size']/1024:.1f} kB" if r["size"] else ("—" if status >= 400 else "cache")
    d.text((900, y+2), size, font=font(17), fill="#5f6368")
    d.text((1080, y+2), "pending" if status >= 400 else "<50 ms", font=font(17), fill="#5f6368")
    d.text((1290, y+2), "localhost:8080" if r["url"].startswith("/") else "cdn.jsdelivr.net", font=font(17), fill="#5f6368")
    y += ROW

img.save(f"{TOOLS}/devtools-network.png")
print("devtools-network.png saved,", len(keep), "rows")
