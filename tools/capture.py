# -*- coding: utf-8 -*-
"""期末大作业截图与测试脚本：对真实运行页面截图并执行测试用例"""
import json, os, sys, time, traceback
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUT, exist_ok=True)
results = []   # 测试用例结果
console_msgs = []  # 控制台消息（调试证据）

def log_result(tid, name, steps, expect, actual, passed):
    results.append({"id": tid, "name": name, "steps": steps,
                    "expect": expect, "actual": actual, "passed": passed})
    print(f"[{'PASS' if passed else 'FAIL'}] {tid} {name}: {actual}")

def settle(page, ms=1200):
    """等待渲染稳定"""
    page.wait_for_timeout(ms)

def safe_goto(page, url, timeout=30000):
    try:
        page.goto(url, wait_until="networkidle", timeout=timeout)
    except Exception:
        page.goto(url, wait_until="load", timeout=timeout)
        page.wait_for_timeout(2500)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)

    # ===== 桌面上下文 =====
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
    page = ctx.new_page()
    page.on("console", lambda m: console_msgs.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)

    # ---------- T1 首页统计 ----------
    safe_goto(page, BASE + "/index.html")
    page.wait_for_selector("#stat-canteens", timeout=20000)
    settle(page, 2500)  # 等待图表与3D渲染
    stats = {
        "canteens": page.text_content("#stat-canteens").strip(),
        "dishes": page.text_content("#stat-dishes").strip(),
        "rooms": page.text_content("#stat-rooms").strip(),
        "seats": page.text_content("#stat-seats").strip(),
    }
    ok = (stats["canteens"] == "5" and stats["dishes"] == "12"
          and stats["rooms"] == "8" and stats["seats"] == "225")
    log_result("T1", "首页统计卡片数据正确", "打开首页，读取4个统计卡片",
               "食堂5、菜品12、自习室8、可用座位225", str(stats), ok)

    # 首页整页截图（含图表与3D）
    page.screenshot(path=f"{OUT}/01-home-desktop.png", full_page=True)
    print("saved 01-home-desktop.png")

    # 图表元素截图
    page.locator("#chart-flow").screenshot(path=f"{OUT}/08-chart-line.png")
    page.locator("#chart-pie").screenshot(path=f"{OUT}/09-chart-pie.png")
    page.locator("#three-container").screenshot(path=f"{OUT}/10-three-scene.png")
    print("saved chart & 3D screenshots")

    # ---------- 食堂页 ----------
    safe_goto(page, BASE + "/pages/cafeteria.html")
    page.wait_for_selector("#dish-tbody tr", timeout=20000)
    settle(page, 1500)
    page.screenshot(path=f"{OUT}/02-cafeteria-desktop.png", full_page=True)
    page.locator("#chart-sales").screenshot(path=f"{OUT}/11-chart-bar.png")
    page.locator("#chart-category").screenshot(path=f"{OUT}/12-chart-category.png")
    print("saved cafeteria screenshots")

    # T2 搜索“肉”
    page.fill("#search-input", "肉")
    page.wait_for_timeout(500)
    rows = page.locator("#dish-tbody tr").count()
    log_result("T2", "菜品搜索过滤", "在搜索框输入“肉”", "表格仅显示名称含“肉”的菜品（红烧肉、牛肉面，共2行）",
               f"过滤后 {rows} 行", rows == 2)

    # T3 搜索不存在 → 空状态
    page.fill("#search-input", "披萨")
    page.wait_for_timeout(500)
    empty_visible = page.locator("#dish-empty").is_visible()
    rows3 = page.locator("#dish-tbody tr").count()
    log_result("T3", "搜索结果为空的空状态提示", "搜索不存在的菜品“披萨”",
               "表格为空并显示“未找到符合条件的菜品”提示", f"空状态可见={empty_visible}，行数={rows3}",
               empty_visible and rows3 == 0)
    # 空状态截图
    page.locator(".table-responsive").screenshot(path=f"{OUT}/05-error-empty.png")
    print("saved empty-state screenshot")

    # T4 分类筛选
    page.fill("#search-input", "")
    page.select_option("#filter-category", "素菜")
    page.wait_for_timeout(500)
    cats = page.locator("#dish-tbody tr td:nth-child(2)").all_text_contents()
    ok4 = len(cats) > 0 and all("素菜" in c for c in cats)
    log_result("T4", "按分类筛选", "分类下拉选择“素菜”", "表格全部为素菜（4个）",
               f"{len(cats)} 行全部为素菜", ok4)
    page.click("#btn-reset")
    page.wait_for_timeout(400)

    # ---------- 自习室页 ----------
    safe_goto(page, BASE + "/pages/studyroom.html")
    page.wait_for_selector("#room-tbody tr", timeout=20000)
    settle(page, 1500)
    page.screenshot(path=f"{OUT}/03-studyroom-desktop.png", full_page=True)
    page.locator("#chart-trend").screenshot(path=f"{OUT}/13-chart-trend.png")
    print("saved studyroom screenshots")

    # T5 空表单校验
    page.click("#btn-add")
    page.wait_for_timeout(600)
    page.click("#btn-save")
    page.wait_for_timeout(500)
    toast5 = page.locator(".toast-container div").last.text_content() if page.locator(".toast-container div").count() else ""
    log_result("T5", "空表单提交校验", "点击“添加自习室”后直接点击“保存”",
               "弹出提示：请完整填写名称、位置、容量和可用座位", toast5, "请完整填写" in toast5)
    page.screenshot(path=f"{OUT}/06-error-invalid.png")  # 视口截图含toast与模态框
    print("saved invalid-input screenshot")

    # T6 非法数值：可用座位 > 容量
    page.fill("#room-name", "测试楼401")
    page.fill("#room-location", "测试楼")
    page.fill("#room-capacity", "50")
    page.fill("#room-available", "80")
    page.click("#btn-save")
    page.wait_for_timeout(500)
    toast6 = page.locator(".toast-container div").last.text_content() if page.locator(".toast-container div").count() else ""
    log_result("T6", "可用座位大于容量的校验", "容量填50，可用座位填80，点击保存",
               "弹出提示：可用座位不能大于总容量，且不保存", toast6, "大于总容量" in toast6)

    # T7 正常添加
    page.fill("#room-available", "20")
    page.click("#btn-save")
    page.wait_for_timeout(800)
    new_row = page.locator("#room-tbody tr", has_text="测试楼401")
    toast7 = page.locator(".toast-container div").last.text_content() if page.locator(".toast-container div").count() else ""
    ok7 = new_row.count() == 1 and "添加成功" in toast7
    log_result("T7", "添加自习室", "填写合法数据（测试楼401/测试楼/50/20）后保存",
               "表格新增一行，弹出“添加成功”", f"新行={new_row.count()}，提示={toast7}", ok7)
    page.screenshot(path=f"{OUT}/04-add-success.png")
    print("saved add-success screenshot")

    # T8 修改自习室
    row = page.locator("#room-tbody tr", has_text="测试楼401")
    row.locator(".btn-edit").click()
    page.wait_for_timeout(600)
    page.fill("#room-available", "10")
    page.click("#btn-save")
    page.wait_for_timeout(800)
    edited = page.locator("#room-tbody tr", has_text="测试楼401").text_content()
    ok8 = "10" in edited
    log_result("T8", "修改自习室", "将测试楼401的可用座位由20改为10并保存",
               "表格中该行可用座位显示10，弹出“修改成功”", edited.replace("\n", " ").strip()[:80], ok8)

    # ---------- 错误处理演示页（网络失败） ----------
    safe_goto(page, BASE + "/test-error.html")
    page.wait_for_timeout(2200)  # 等待自动触发 + toast出现
    toast9 = ""
    for el in page.locator(".toast-container div").all():
        t = el.text_content()
        if "数据加载失败" in t:
            toast9 = t
    log_result("T9", "JSON网络失败处理", "打开错误演示页，自动请求不存在的 data/not-exist.json",
               "右上角弹出红色提示“数据加载失败…”，控制台输出错误，页面其余功能不受影响", toast9,
               "数据加载失败" in toast9)
    page.screenshot(path=f"{OUT}/07-error-network.png")
    print("saved network-error screenshot")

    ctx.close()

    # ===== 移动端上下文 =====
    mctx = browser.new_context(viewport={"width": 390, "height": 844},
                               device_scale_factor=2, is_mobile=True,
                               user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1")
    mp = mctx.new_page()
    safe_goto(mp, BASE + "/index.html")
    mp.wait_for_selector("#stat-canteens", timeout=20000)
    mp.wait_for_timeout(2500)

    # T10 移动端导航折叠
    tog_visible = mp.locator(".navbar-toggler").is_visible()
    menu_hidden = not mp.locator("#navMenu").is_visible()
    mp.click(".navbar-toggler")
    mp.wait_for_timeout(600)
    menu_shown = mp.locator("#navMenu").is_visible()
    log_result("T10", "移动端导航折叠与展开", "390px宽视口打开首页，点击汉堡按钮",
               "折叠按钮可见，菜单默认收起，点击后展开", f"按钮可见={tog_visible}，初始收起={menu_hidden}，点击后展开={menu_shown}",
               tog_visible and menu_hidden and menu_shown)

    mp.screenshot(path=f"{OUT}/14-home-mobile.png", full_page=True)
    print("saved mobile home screenshot")

    safe_goto(mp, BASE + "/pages/studyroom.html")
    mp.wait_for_selector("#room-tbody tr", timeout=20000)
    mp.wait_for_timeout(1500)
    mp.screenshot(path=f"{OUT}/15-studyroom-mobile.png", full_page=True)
    print("saved mobile studyroom screenshot")
    mctx.close()

    browser.close()

# 保存测试结果与控制台消息
with open(f"{OUT}/test-results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
with open(f"{OUT}/console-messages.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(console_msgs) if console_msgs else "（无 error/warning 级别消息）")

npass = sum(1 for r in results if r["passed"])
print(f"\n===== 测试完成: {npass}/{len(results)} 通过 =====")
