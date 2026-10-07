# -*- coding: utf-8 -*-
"""生成文档所需图片素材：设计思路图、Git记录图、控制台调试图"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont

TOOLS = os.path.dirname(os.path.abspath(__file__))
FONT = "C:\\Windows\\Fonts\\msyh.ttc"      # 微软雅黑
FONT_B = "C:\\Windows\\Fonts\\msyhbd.ttc"  # 微软雅黑粗体

def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)

# ============ 1. 设计思路图 ============
def draw_arch():
    W, H = 1500, 1150
    img = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(img)

    def rbox(x1, y1, x2, y2, fill, outline, radius=14, width=2):
        d.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill,
                            outline=outline, width=width)

    def center_text(cx, cy, text, f, color="#1e293b"):
        bb = d.textbbox((0, 0), text, font=f)
        d.text((cx - (bb[2]-bb[0])/2, cy - (bb[3]-bb[1])/2), text, font=f, fill=color)

    def arrow_down(cx, y1, y2, color="#64748b"):
        d.line([cx, y1, cx, y2-10], fill=color, width=3)
        d.polygon([(cx-8, y2-12), (cx+8, y2-12), (cx, y2)], fill=color)

    # 标题
    center_text(W/2, 45, "“校园生活服务数据中心”设计思路图", font(34, True), "#0f172a")

    # 用户层
    rbox(430, 95, 1070, 165, "#eff6ff", "#2563eb")
    center_text(W/2, 130, "用户（手机端 / 桌面端，响应式适配）", font(24, True), "#1d4ed8")

    arrow_down(W/2, 165, 215)

    # 页面层
    rbox(70, 215, 1430, 390, "#f8fafc", "#94a3b8")
    center_text(W/2, 240, "页面层（3个页面，顶部导航栏互相跳转）", font(20, True), "#475569")
    pw = 380
    x1, x2, x3 = 120, 560, 1000
    rbox(x1, 275, x1+pw, 355, "#dbeafe", "#3b82f6")
    center_text(x1+pw/2, 300, "首页 index.html", font(22, True), "#1e40af")
    center_text(x1+pw/2, 332, "统计卡片｜人流折线图｜分类饼图", font(17), "#475569")
    rbox(x2, 275, x2+pw, 355, "#dcfce7", "#22c55e")
    center_text(x2+pw/2, 300, "食堂数据 cafeteria.html", font(22, True), "#166534")
    center_text(x2+pw/2, 332, "食堂卡片｜菜品搜索筛选｜销量图表", font(17), "#475569")
    rbox(x3, 275, x3+pw, 355, "#fef3c7", "#f59e0b")
    center_text(x3+pw/2, 300, "自习室管理 studyroom.html", font(22, True), "#92400e")
    center_text(x3+pw/2, 332, "座位查询｜添加/修改表单｜趋势图表", font(17), "#475569")
    center_text(W/2, 372, "三维展示区（首页内嵌）：Three.js 校园建筑场景，可拖拽旋转 / 滚轮缩放", font(17), "#7c3aed")

    arrow_down(W/2, 390, 440)

    # 脚本层
    rbox(70, 440, 1430, 610, "#f8fafc", "#94a3b8")
    center_text(W/2, 465, "脚本层（js/ 目录，职责分离）", font(20, True), "#475569")
    sw = 260
    xs = [120, 420, 720, 1020]
    labels = [("common.js", "JSON加载｜Toast提示\n格式化｜星级渲染"),
              ("index.js", "首页统计与图表渲染"),
              ("cafeteria.js\nstudyroom.js", "搜索/筛选/增改\n图表渲染"),
              ("three-scene.js", "三维校园场景\n建筑/树木/光照")]
    fills = [("#ede9fe", "#7c3aed"), ("#fce7f3", "#db2777"), ("#dcfce7", "#16a34a"), ("#ffedd5", "#ea580c")]
    for (x, (t, sub), (fl, ol)) in zip(xs, labels, fills):
        rbox(x, 490, x+sw, 585, fl, ol)
        tsize = 19 if "\n" not in t else 17
        bb = d.multiline_textbbox((0, 0), t, font=font(tsize, True), align="center")
        d.text((x+sw/2-(bb[2]-bb[0])/2, 498), t, font=font(tsize, True), fill="#0f172a", align="center")
        ty = 538 if "\n" not in t else 552
        bb2 = d.multiline_textbbox((0, 0), sub, font=font(15), align="center")
        d.text((x+sw/2-(bb2[2]-bb2[0])/2, ty), sub, font=font(15), fill="#475569", align="center")

    arrow_down(W/2, 610, 660)

    # 库层
    rbox(70, 660, 1430, 780, "#f1f5f9", "#94a3b8")
    center_text(W/2, 685, "第三方库（CDN 引入）", font(20, True), "#475569")
    lw = 300
    libs = [("Bootstrap 5", "响应式栅格布局"), ("jQuery 3.7", "DOM操作与AJAX"),
            ("ECharts 5.4", "折线/柱状/饼图"), ("Three.js 0.160", "三维场景+轨道控制器")]
    lx = [120, 460, 800, 1140]
    for x, (t, sub) in zip(lx, libs):
        rbox(x, 705, x+lw, 755, "#ffffff", "#64748b")
        center_text(x+lw/2, 720, t, font(18, True), "#0f172a")
        center_text(x+lw/2, 742, sub, font(14), "#64748b")

    arrow_down(W/2, 780, 830)

    # 数据层
    rbox(70, 830, 1430, 950, "#f8fafc", "#94a3b8")
    center_text(W/2, 855, "数据层（本地 JSON，$.getJSON 加载，无后端服务器）", font(20, True), "#475569")
    rbox(240, 880, 700, 930, "#e0f2fe", "#0284c7")
    center_text(470, 905, "data/cafeteria.json  食堂/菜品/客流/分类销量", font(18), "#075985")
    rbox(800, 880, 1260, 930, "#e0f2fe", "#0284c7")
    center_text(1030, 905, "data/studyroom.json  自习室/座位/趋势/楼栋统计", font(18), "#075985")

    # 底部说明
    center_text(W/2, 1000, "数据流：$.getJSON 加载 JSON → jQuery 解析渲染卡片与表格 → ECharts 渲染图表", font(20), "#334155")
    center_text(W/2, 1040, "错误流：请求失败/空数据/非法输入 → Toast 提示 / 空状态 / 表单校验", font(20), "#b91c1c")

    img.save(f"{TOOLS}/design-arch.png")
    print("design-arch.png saved")

# ============ 2. Git 记录终端图 ============
def draw_gitlog():
    with open(f"{TOOLS}/gitlog.txt", encoding="utf-8-sig") as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    title = "> git log --oneline --decorate"
    W, LH, PAD = 1500, 52, 40
    H = PAD*2 + 70 + LH*len(lines)
    img = Image.new("RGB", (W, H), "#1e1e2e")
    d = ImageDraw.Draw(img)
    f_cmd = font(26)
    f_log = font(26)
    # 终端圆点
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        d.ellipse([PAD+i*36, 22, PAD+i*36+22, 44], fill=c)
    d.text((PAD, 70), title, font=f_cmd, fill="#89ddff")
    y = 120
    colors = {"hash": "#c3e88d", "head": "#ff9cac", "text": "#eaeaea"}
    for line in lines:
        line = line.strip()
        parts = line.split(" ", 2)
        d.text((PAD, y), parts[0], font=f_log, fill=colors["hash"])
        x = PAD + d.textlength(parts[0], font=f_log) + 14
        rest = line[len(parts[0]):].strip()
        if "(HEAD" in rest or "origin/" in rest:
            end = rest.index(")")+1
            deco = rest[:end]
            d.text((x, y), deco, font=f_log, fill=colors["head"])
            x += d.textlength(deco, font=f_log) + 12
            rest = rest[end:].strip()
        d.text((x, y), rest, font=f_log, fill=colors["text"])
        y += LH
    img.save(f"{TOOLS}/git-log.png")
    print("git-log.png saved")

# ============ 3. 控制台调试图 ============
def draw_console():
    with open(f"{TOOLS}/screenshots/console-messages.txt", encoding="utf-8") as f:
        msgs = [l.rstrip("\n") for l in f if l.strip()]
    W, LH, PAD = 1560, 0, 28
    f_msg = font(21)
    # 临时画布用于测量文本宽度
    _tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    def d_textlen(t, f):
        return _tmp.textlength(t, font=f)
    # 手动换行长消息
    wrapped = []
    for m in msgs:
        maxw = W - PAD*2 - 60
        cur = ""
        for ch in m:
            cur += ch
            if d_textlen(cur, f_msg) > maxw:
                wrapped.append(cur)
                cur = ""
        wrapped.append(cur) if cur else None
    LH = 40
    H = 96 + LH*len(wrapped) + PAD
    img = Image.new("RGB", (W, H), "#1e1e1e")
    d = ImageDraw.Draw(img)

    # 标题栏
    d.rectangle([0, 0, W, 56], fill="#2d2d2d")
    d.text((PAD, 14), "DevTools - Console（控制台消息记录）", font=font(22, True), fill="#e0e0e0")
    d.text((W-330, 14), "Default levels  ✓ Errors  ✓ Warnings", font=font(18), fill="#9e9e9e")
    y = 72
    for m in wrapped:
        if m.startswith("[warning]"):
            d.rectangle([0, y-4, W, y+LH-8], fill="#2a2410")
            d.text((PAD, y), "⚠", font=f_msg, fill="#ffd54f")
            d.text((PAD+30, y), m[len("[warning] "):], font=f_msg, fill="#ffe082")
        elif m.startswith("[error]"):
            d.rectangle([0, y-4, W, y+LH-8], fill="#2c1518")
            d.text((PAD, y), "✕", font=f_msg, fill="#ff8a80")
            d.text((PAD+30, y), m[len("[error] "):], font=f_msg, fill="#ff8a80")
        else:
            d.text((PAD, y), m, font=f_msg, fill="#e0e0e0")
        y += LH
    img.save(f"{TOOLS}/devtools-console.png")
    print("devtools-console.png saved")

draw_arch()
draw_gitlog()
draw_console()
