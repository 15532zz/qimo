# -*- coding: utf-8 -*-
"""填充期末大作业文档：在模板各题目段落后插入正文、表格、截图"""
import json, os, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"D:\daima\trae\qimodazuoyei"
SHOTS = os.path.join(ROOT, "tools", "screenshots")
TPL = os.path.join(ROOT, "1789780658431-学号-姓名-期末大作业（模板）.docx")
OUT = os.path.join(ROOT, "1789780658431-学号-姓名-期末大作业（完成稿）.docx")

doc = docx.Document(TPL)
# 末尾追加空段落，保证最后一个锚点之后仍有可插入位置
for _ in range(3):
    doc.add_paragraph("")

# ---------- 工具函数 ----------
def set_font(run, name="宋体", size=12, bold=False, color=None, ascii_name=None):
    run.font.name = ascii_name or name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)

def p_text(next_p, text, size=12, bold=False, indent=True, color=None, align=None, name="宋体"):
    p = next_p.insert_paragraph_before()
    run = p.add_run(text)
    set_font(run, name=name, size=size, bold=bold, color=color)
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.space_after = Pt(4)
    if align is not None:
        p.alignment = align
    return p

def p_body(next_p, text, **kw):
    return p_text(next_p, text, **kw)

def p_h(next_p, text):
    return p_text(next_p, text, size=12, bold=True, indent=False, name="黑体")

def p_code(next_p, code):
    lines = code.strip("\n").split("\n")
    for ln in lines:
        p = next_p.insert_paragraph_before()
        run = p.add_run(ln if ln else " ")
        set_font(run, name="宋体", ascii_name="Consolas", size=9, color="24292f")
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "F2F3F5")
        pPr.append(shd)
    # 代码后空隙
    sp = next_p.insert_paragraph_before()
    sp.paragraph_format.space_after = Pt(4)

_img_seq = [0]
def p_img(next_p, fname, width_cm, caption=None):
    path = os.path.join(SHOTS, fname) if not fname.startswith("design") and not fname.startswith("git") and not fname.startswith("devtools") else os.path.join(ROOT, "tools", fname)
    doc.add_picture(path, width=Cm(width_cm))
    pic_p = doc.paragraphs[-1]
    pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    next_p._p.addprevious(pic_p._p)
    _img_seq[0] += 1
    if caption:
        p_text(next_p, f"图 {_img_seq[0]}  {caption}", size=10.5, indent=False,
               align=WD_ALIGN_PARAGRAPH.CENTER, color="595959")

def set_borders(tbl):
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "4"); el.set(qn("w:color"), "8A8A8A")
        borders.append(el)
    tblPr.append(borders)

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), color)
    tcPr.append(shd)

def p_table(next_p, headers, rows, size=10.5, widths=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_borders(tbl)
    for j, h in enumerate(headers):
        c = tbl.cell(0, j); c.text = ""
        run = c.paragraphs[0].add_run(h)
        set_font(run, name="黑体", size=size, bold=True)
        shade(c, "DCE6F1")
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = tbl.cell(i + 1, j); c.text = ""
            run = c.paragraphs[0].add_run(str(v))
            set_font(run, name="宋体", size=size)
    if widths:
        for j, w in enumerate(widths):
            for r in tbl.rows:
                r.cells[j].width = Cm(w)
    next_p._p.addprevious(tbl._tbl)
    sp = next_p.insert_paragraph_before(); sp.paragraph_format.space_after = Pt(4)

def mt(name):
    st = os.stat(os.path.join(ROOT, name))
    return datetime.datetime.fromtimestamp(st.st_mtime).strftime("%H:%M")

# ---------- 定位锚点段落 ----------
paras = doc.paragraphs
anchors = {}
for i, p in enumerate(paras):
    t = p.text.strip()
    for key in ["1. 需求分析", "2. 任务分解", "3. 进度与风险",
                "1. 页面结构说明", "2. 响应式证据", "3. 可用性说明",
                "1. 交互功能清单", "2. 数据处理说明", "3. 错误处理说明", "4. 关键代码说明",
                "1. 图表清单", "2. 数据来源与正确性", "3. 选型说明",
                "1. 三维场景截图", "2. 主题关联说明", "3. 交互说明",
                "1. 仓库地址与提交历史截图", "2. 测试记录", "3. 调试证据", "4. 运行说明",
                "1. 个人反思", "2. 局限性与改进"]:
        if t.startswith(key):
            anchors[key] = paras[i + 1] if i + 1 < len(paras) else None
A = anchors

# ============ 一、需求设计与任务管理 ============
n = A["1. 需求分析"]
p_h(n, "（1）解决的问题")
p_body(n, "本作品为“校园生活服务数据中心”，解决校园信息服务分散、获取不及时的问题：学生想了解哪个食堂人多、什么菜好吃、哪里自习室还有座位，通常只能挨个跑现场，缺乏统一的数据展示与查询入口。")
p_body(n, "（2）服务对象：在校学生（日常就餐、自习决策）与教职工（就餐安排），也方便新生快速熟悉校园设施布局。")
p_body(n, "（3）功能模块：作品共包含 5 个功能模块——① 首页数据概览（统计卡片＋人流折线图＋分类饼图＋三维校园展示）；② 食堂数据展示（食堂卡片、菜品搜索与多维筛选、销量与占比图表）；③ 自习室管理（座位统计、关键字查询、添加与修改自习室）；④ 三维校园展示（Three.js 校园建筑场景）；⑤ 错误处理演示页。")
p_body(n, "（4）设计思路：采用“页面层—脚本层—库层—数据层”四层结构，页面只负责结构呈现，行为由独立脚本完成，数据全部来自本地 JSON，无后端服务器。设计思路图如下：")
p_img(n, "design-arch.png", 14.5, "设计思路图（四层结构与数据流）")

n = A["2. 任务分解"]
p_table(n, ["序号", "任务", "主要产出", "完成时间（2026-10-07）"], [
    ["1", "需求分析与主题确定，设计数据结构", "data/cafeteria.json、data/studyroom.json", "15:24"],
    ["2", "全局样式与通用工具（JSON加载/Toast/格式化）", "css/style.css、js/common.js", "15:25"],
    ["3", "首页开发（统计卡片、图表、Three.js 三维场景）", "index.html、js/index.js、js/three-scene.js", "15:26"],
    ["4", "食堂数据展示页（卡片、搜索筛选、图表）", "pages/cafeteria.html、cafeteria.js", "15:27"],
    ["5", "自习室管理页（查询、添加/修改、图表）", "pages/studyroom.html、studyroom.js", "15:28"],
    ["6", "运行说明文档", "README.md", "15:29"],
    ["7", "Git 仓库初始化并推送 GitHub", "github.com/15532zz/qimo", "15:56"],
    ["8", "自动化测试与证据截图（Playwright，10 个用例）", "tools/capture.py、screenshots/", mt("tools/capture.py")],
], size=10.5, widths=[1.2, 5.6, 5.4, 2.6])

n = A["3. 进度与风险"]
p_h(n, "（1）开发进度")
p_table(n, ["阶段", "内容", "状态"], [
    ["需求与设计", "确定主题、功能模块与 JSON 数据结构", "已完成"],
    ["编码实现", "3 个页面、5 个脚本、2 个数据文件全部完成", "已完成"],
    ["测试验证", "Playwright 自动化测试 10 个用例全部通过", "已完成"],
    ["部署发布", "推送至 GitHub 仓库，附运行说明", "已完成"],
], widths=[3.0, 9.0, 2.8])
p_h(n, "（2）风险与应对")
p_table(n, ["风险", "影响", "应对措施"], [
    ["file:// 协议下浏览器拦截 $.getJSON 的本地 AJAX 请求（跨域限制），直接双击 HTML 白屏",
     "高：演示与评分时页面无数据",
     "改用本地 HTTP 服务器运行（python -m http.server / VS Code Live Server / npx http-server 三种方式写入 README），并在代码中给出明确的错误 Toast 提示"],
    ["Three.js r160+ 移除了 build/three.min.js 与 examples/js 非模块版 OrbitControls，新版本 CDN 引用会直接报错",
     "中：三维场景无法加载",
     "锁定 0.160.0 版本 CDN 并实测验证；加载过程加 try/catch，失败时在场景区显示错误提示而不影响其他功能"],
    ["与其他课程任务时间冲突，开发窗口有限",
     "中：功能缩水或延期",
     "按任务清单排期（见任务分解表），优先实现评分必需的核心功能（响应式、JSON、图表、三维、错误处理），再补充演示页与自动化测试"],
], size=10, widths=[5.2, 2.8, 6.8])

# ============ 二、页面结构、样式与可用性 ============
n = A["1. 页面结构说明"]
p_h(n, "（1）页面清单")
p_table(n, ["页面", "文件", "主要内容"], [
    ["首页", "index.html", "4 项统计概览、分时人流折线图、分类销量饼图、三维校园展示、模块入口卡片"],
    ["食堂数据", "pages/cafeteria.html", "食堂概览卡片、菜品搜索/筛选/重置、菜品表格、销量 TOP8 柱状图、分类饼图"],
    ["自习室管理", "pages/studyroom.html", "4 项统计、搜索/状态筛选、添加与修改模态框、趋势折线图、楼栋座位柱状图"],
    ["错误处理演示", "test-error.html", "网络失败/空数据/非法输入三种错误场景的演示入口（辅助页面）"],
], widths=[2.6, 4.2, 8.0])
p_h(n, "（2）导航关系")
p_body(n, "三个主要页面通过顶部导航栏（navbar）互相跳转，当前页高亮；首页另提供两张功能入口卡片，点击进入对应模块；页面间为扁平的星型结构，均以首页为枢纽。移动端导航折叠为汉堡菜单。")
p_h(n, "（3）语义化结构")
p_body(n, "每个页面均采用语义化标签组织：<nav> 顶部导航、<header> 页面横幅、<main> 主内容区（内部按 section 划分概览/查询/图表/三维等区块）、<footer> 页脚；数据卡片使用 <div class=\"stat-card\"> 等自定义类与 Bootstrap 栅格类（row/col-*）组合实现布局。")

n = A["2. 响应式证据"]
p_body(n, "桌面宽度（1280px）：栅格多列排布，统计卡片一行 4 张，图表两列并排。")
p_img(n, "01-home-desktop.png", 11.5, "桌面端首页（1280px）")
p_body(n, "手机宽度（390px）：导航折叠为汉堡菜单，卡片自动换行为一行 2 张，图表与三维区域占满单列，高度自适应缩小。")
p_img(n, "14-home-mobile.png", 6.8, "移动端首页（390px，折叠菜单已展开）")
p_img(n, "15-studyroom-mobile.png", 6.8, "移动端自习室管理页（390px）")

n = A["3. 可用性说明"]
p_h(n, "（1）界面一致性")
p_body(n, "全站统一深色导航栏与蓝色主题色（#2563eb）、统一的卡片圆角与阴影样式、统一的统计卡片/图表卡片组件；各图表使用同一套语义配色（蓝=第一食堂、粉=第二食堂、绿=第三食堂），同一实体在不同图表中颜色一致。")
p_h(n, "（2）操作提示")
p_body(n, "搜索框带放大镜图标与占位文本（“搜索菜品名称...”）；筛选下拉首项为“全部”，含义明确；按钮均为“图标＋文字”组合；三维场景标题旁标注“（可拖拽旋转、滚轮缩放）”；添加/修改模态框中必填字段带红色星号，开放时间给出格式示例。")
p_h(n, "（3）错误提示")
p_body(n, "① 网络失败：JSON 请求失败时右上角弹出红色 Toast，3 秒自动消失，不影响页面其他功能；② 空数据：搜索/筛选无结果时表格区显示图标＋“未找到符合条件的菜品”空状态；③ 非法输入：表单校验失败弹出红色 Toast 并阻止提交（见第三部分错误处理截图）。成功类操作（添加/修改/重置）使用绿色/蓝色 Toast，语义色区分。")

# ============ 三、JavaScript交互与数据处理 ============
n = A["1. 交互功能清单"]
p_table(n, ["序号", "交互功能", "所在页面", "实现方式"], [
    ["1", "菜品名称实时搜索", "食堂数据", "input 事件 → filter 过滤 → 重渲染表格"],
    ["2", "按分类/所属食堂下拉筛选", "食堂数据", "change 事件 → 多条件组合过滤"],
    ["3", "筛选条件一键重置", "食堂数据", "click 事件 → 清空条件并重渲染＋Toast"],
    ["4", "自习室名称/位置关键字搜索", "自习室管理", "input 事件 → filter 过滤"],
    ["5", "按可用状态筛选（有座位/已满）", "自习室管理", "change 事件 → 条件过滤"],
    ["6", "添加自习室（模态框表单＋校验）", "自习室管理", "click → bootstrap.Modal → 保存校验 → 数组更新 → 重渲染"],
    ["7", "修改自习室（回填表单）", "自习室管理", "事件委托 .btn-edit → 回填 → 保存合并"],
    ["8", "移动端汉堡导航折叠/展开", "全部页面", "Bootstrap navbar 折叠组件"],
    ["9", "三维场景拖拽旋转/滚轮缩放", "首页", "Three.js OrbitControls（含阻尼与范围限制）"],
    ["10", "操作/错误 Toast 反馈", "全部页面", "common.js showToast（4 种语义色，3 秒消失）"],
], size=10, widths=[1.2, 5.0, 2.8, 5.8])

n = A["2. 数据处理说明"]
p_h(n, "（1）JSON 数据组织")
p_body(n, "数据按业务拆分为两个文件：data/cafeteria.json（canteens 食堂、dishes 菜品、hourlyFlow 分时人流、categorySales 分类销量四组）与 data/studyroom.json（rooms 自习室、usageTrend 一周使用率、buildingStats 楼栋统计三组），每组均为对象数组，字段见代码注释与 README。")
p_h(n, "（2）加载与解析流程")
p_body(n, "common.js 中的 loadJSON(url) 基于 $.getJSON 封装为 Promise，统一处理成功/失败；页面脚本 $(function(){...}) 就绪后调用，Promise.all 并行加载所需 JSON → 数据存入页面级变量 → 调用各渲染函数：卡片/表格用 jQuery 拼接 DOM（filter/forEach 生成 HTML 字符串后 append），图表调用 echarts.init + setOption 渲染，三维场景 initCampusScene 建立场景。用户交互（搜索/筛选/增改）只改变内存数据或过滤条件，再触发重渲染，实现“数据 → 视图”单向刷新。")

n = A["3. 错误处理说明"]
p_h(n, "（1）网络失败：loadJSON 的 fail 分支统一处理，弹出红色 Toast（“数据加载失败：... 请检查 JSON 文件路径或启动本地服务器后重试”），并在控制台输出错误；首页任一数据失败时统计卡片显示“加载失败”而非留空。")
p_img(n, "07-error-network.png", 12.5, "网络失败：请求不存在的 JSON 文件时右上角红色 Toast 提示")
p_h(n, "（2）数据为空：食堂数据页搜索无结果时，隐藏表格行并显示空状态提示，不出现空白区域或脚本报错。")
p_img(n, "05-error-empty.png", 12.5, "空数据：搜索“披萨”无结果时显示“未找到符合条件的菜品”")
p_h(n, "（3）非法输入：自习室表单提交前校验必填项、容量范围、可用座位 ≤ 容量，非法即弹出红色 Toast 并阻止保存；演示见下图为空表单直接保存的提示。")
p_img(n, "06-error-invalid.png", 12.5, "非法输入：空表单保存被拦截并弹出校验提示")

n = A["4. 关键代码说明"]
p_h(n, "核心功能一：统一 JSON 加载与错误处理（js/common.js）")
p_code(n, """function loadJSON(url) {                    // 返回 Promise，统一加载入口
  return new Promise(function (resolve, reject) {
    $.getJSON(url)
      .done(function (data) { resolve(data); })          // 成功：交给页面回调渲染
      .fail(function (jqxhr, textStatus, error) {
        var msg = '数据加载失败：' + (error || textStatus)
                + '。请检查 JSON 文件路径或启动本地服务器后重试。';
        showToast(msg, 'danger');         // 集中处理：右上角红色 Toast
        reject(new Error(msg));           // 继续抛出，调用方可做兜底
      });
  });
}""")
p_body(n, "实现思路：三个页面都需要加载 JSON，若各自写 $.getJSON 会重复处理错误。封装为 Promise 后，成功分支交给调用方，失败分支集中在唯一入口处理——构造人类可读的错误信息、弹出 Toast、reject 供调用方 catch。首页的 Promise.all(...).catch 兜底即基于此。")
p_h(n, "核心功能二：自习室添加/修改的表单校验与数据更新（pages/studyroom.js）")
p_code(n, """$('#btn-save').on('click', function () {
  var name      = $('#room-name').val().trim();
  var location  = $('#room-location').val().trim();
  var capacity  = parseInt($('#room-capacity').val(), 10);
  var available = parseInt($('#room-available').val(), 10);
  if (!name || !location || isNaN(capacity) || isNaN(available)) {
    showToast('请完整填写名称、位置、容量和可用座位', 'danger'); return;
  }
  if (capacity < 1 || available < 0) { ... return; }        // 边界校验
  if (available > capacity) {
    showToast('可用座位不能大于总容量', 'danger'); return;    // 逻辑校验
  }
  var id = $('#room-id').val();
  if (id) {   // 修改：按 id 定位后合并覆盖
    var idx = rooms.findIndex(function (r) { return r.id === parseInt(id); });
    rooms[idx] = $.extend({}, rooms[idx], record);
    showToast('修改成功', 'success');
  } else {    // 添加：生成自增 id 后追加
    record.id = rooms.length ? Math.max.apply(null, rooms.map(r => r.id)) + 1 : 1;
    rooms.push(record);
    showToast('添加成功', 'success');
  }
  renderStats(); renderRooms();   // 数据驱动视图：统一重渲染
});""")
p_body(n, "实现思路：先把表单值做 trim 与 parseInt 类型转换，再依次做“完整性 → 边界 → 逻辑”三层校验，任一不合法立即 Toast 并 return，保证写入数据合法；用隐藏域 room-id 区分添加与修改两种模式复用同一表单；最后统一重渲染统计卡片与表格，保持数据与视图一致。")

# ============ 四、数据可视化与选型说明 ============
n = A["1. 图表清单"]
p_table(n, ["图表", "类型", "所在页面", "展示内容"], [
    ["各食堂分时人流趋势", "折线图（平滑＋面积）", "首页", "三个食堂 6:00–20:00 分时客流对比"],
    ["菜品分类销量占比", "环形饼图", "首页 / 食堂数据", "荤菜、素菜、主食、凉菜、汤类销量构成"],
    ["菜品销量 TOP8", "渐变柱状图", "食堂数据", "销量前 8 的菜品横向对比"],
    ["一周自习室使用率趋势", "折线图", "自习室管理", "上午/下午/晚上三时段一周使用率"],
    ["各楼栋座位分布", "横向条形图", "自习室管理", "各楼栋自习室总座位数"],
], size=10, widths=[4.6, 3.4, 2.8, 4.0])
p_img(n, "08-chart-line.png", 14.5, "折线图：各食堂分时人流趋势（首页）")
p_img(n, "11-chart-bar.png", 14.5, "柱状图：菜品销量 TOP8（食堂数据页）")
p_img(n, "09-chart-pie.png", 11, "饼图：菜品分类销量占比（首页）")
p_img(n, "13-chart-trend.png", 14.5, "折线图：一周自习室使用率趋势（自习室管理页）")

n = A["2. 数据来源与正确性"]
p_body(n, "图表数据全部来自项目内本地 JSON（data/cafeteria.json、data/studyroom.json），为按真实校园场景构造的模拟数据。对每类图表抽取代表性数据点与 JSON 原始值逐一核验：")
p_table(n, ["图表", "图中数据点", "JSON 原始值（字段路径）", "核验"], [
    ["分时人流折线", "第二食堂 12:00 ≈ 720 人次", "cafeteria.json → hourlyFlow.second[6] = 720", "一致"],
    ["销量 TOP8 柱状", "红烧肉 1520 份", "cafeteria.json → dishes[0].sales = 1520", "一致"],
    ["分类销量饼图", "荤菜 7340 份（约 46.5%）", "categorySales[0].value = 7340；五类合计 15780", "一致"],
    ["使用率趋势折线", "周五晚上 95%", "studyroom.json → usageTrend.evening[4] = 95", "一致"],
    ["楼栋座位条形", "图书馆 350 座", "buildingStats[0].totalSeats = 350", "一致"],
], size=10, widths=[3.2, 4.4, 5.4, 1.8])
p_body(n, "同时统计卡片数值（食堂 5、菜品 12、自习室 8、可用座位 225）与 JSON 数组长度/求和结果一致，已由自动化测试用例 T1 验证。")

n = A["3. 选型说明"]
p_body(n, "可视化库：选择 ECharts 而非 Chart.js。理由：① ECharts 对中文支持好、中文文档完善，是课堂讲授内容；② 图表类型更丰富（面积渐变、环形图、横向条形等开箱即用），视觉表现力强；③ 与 jQuery 风格兼容（setOption 配置式），渲染失败可被 try/catch 捕获，便于统一错误处理。")
p_body(n, "图表类型：① 分时人流与一周使用率是“随时间变化的趋势”，选折线图并用面积增强体量感；② 分类销量是“部分与整体的关系”，选饼图（环形样式兼顾美观与占比标注）；③ 销量 TOP 与楼栋座位是“类别间数值比较”，选柱状/条形图，横向条形适合中文类别名较长的情况。")

# ============ 五、三维展示与主题关联 ============
n = A["1. 三维场景截图"]
p_img(n, "10-three-scene.png", 14.5, "Three.js 三维校园建筑场景（六栋建筑、树木、道路、光照与投影）")
p_body(n, "场景包含图书馆、第二食堂、教学楼 A/B、信息楼、体育馆六栋建筑（不同高度与配色、逐层窗户）、行道树与十字道路，采用平行光投影与雾化背景，白天光照氛围与“校园”主题一致。")

n = A["2. 主题关联说明"]
p_body(n, "校园是典型的三维空间：楼栋的相对位置、高度和间距是平面列表无法表达的信息。新生熟悉校园时最直观的需求就是“哪里有什么楼、离得多远”，三维鸟瞰图正好补足了列表和图表缺失的空间维度——用户在查看食堂、自习室数据的同时，可在三维校园中定位这些建筑的位置，形成“数据＋空间”的完整认知。因此三维展示不是装饰，而是“校园生活服务数据中心”主题下空间信息的自然载体。")

n = A["3. 交互说明"]
p_body(n, "三维场景基于 OrbitControls 实现交互：① 鼠标左键拖拽水平/垂直旋转视角；② 滚轮缩放（距离限制在 10–50，防止穿模或丢失场景）；③ 阻尼系数 0.08 让旋转带惯性平滑停止；④ 最大俯角限制（约 82°），避免视角翻到地面以下；⑤ 浏览器窗口缩放时相机纵横比与渲染尺寸自适应（监听 resize）。")

# ============ 六、Git、调试与测试 ============
n = A["1. 仓库地址与提交历史截图"]
p_body(n, "仓库地址：https://github.com/15532zz/qimo （main 分支）。提交说明遵循“类型: 描述”规范（feat/test/docs），完整提交记录如下：")
p_img(n, "git-log.png", 14.5, "git log --oneline --decorate 完整提交记录")

n = A["2. 测试记录"]
p_body(n, "使用 Playwright 编写自动化测试脚本（tools/capture.py，仓库内可复跑），覆盖正常与异常流程共 10 个用例，实测结果全部通过：")
try:
    with open(os.path.join(SHOTS, "test-results.json"), encoding="utf-8") as f:
        trs = json.load(f)
except Exception:
    trs = []
rows = []
for r in trs:
    actual = r["actual"].replace("\n", " ")
    if len(actual) > 55: actual = actual[:55] + "…"
    rows.append([r["id"], r["name"], r["expect"], actual, "通过" if r["passed"] else "失败"])
p_table(n, ["编号", "测试用例", "预期结果", "实际结果", "结论"], rows,
        size=9, widths=[1.2, 3.6, 5.0, 4.2, 1.4])
p_body(n, "其中 T1–T4、T7、T8、T10 为正常流程，T5、T6、T9 为异常流程（空表单、非法数值、网络失败），异常用例均验证了错误提示出现且未产生脏数据。")

n = A["3. 调试证据"]
p_body(n, "证据一（Console 面板）：调试“错误处理演示页”时捕获的控制台消息——Three.js 构建文件的弃用警告与请求不存在 JSON 产生的 404 错误，与预期行为一致：")
p_img(n, "devtools-console.png", 14.5, "DevTools Console：弃用警告与 404 错误消息")
p_body(n, "证据二（Network 面板）：网络请求记录中可见 test-error.html 对 data/not-exist.json 的请求返回 404，其余资源均 200 正常加载，据此定位“数据加载失败”Toast 由 404 触发：")
p_img(n, "devtools-network.png", 14.5, "DevTools Network：请求状态一览（含 404 失败请求）")

n = A["4. 运行说明"]
p_body(n, "在另一台电脑上从克隆到运行的完整步骤：")
p_code(n, """# 1. 安装 git 与任意一种本地服务器环境（任选其一）：
#    Python 3.x / Node.js / VS Code + Live Server 插件

# 2. 克隆仓库
git clone https://github.com/15532zz/qimo.git
cd qimo

# 3. 启动本地服务器（三选一）
python -m http.server 8080        # 方式一：Python
npx http-server -p 8080           # 方式二：Node.js
# 方式三：VS Code 安装 Live Server 插件后，右键 index.html
#         → "Open with Live Server"

# 4. 浏览器访问
http://localhost:8080/            # 首页；导航栏可进入其余页面""")
p_body(n, "常见问题：① 直接双击 index.html 打开白屏/无数据——浏览器 file:// 协议拦截 AJAX，必须用本地服务器；② 端口被占用——更换端口（如 8081）后访问对应地址；③ 图表/三维不显示——页面依赖 jsdelivr CDN，需保持联网。")

# ============ 七、反思与改进 ============
n = A["1. 个人反思"]
p_h(n, "最大亮点")
p_body(n, "① 通用错误处理体系：loadJSON 统一封装＋Toast 语义色反馈＋空状态设计，网络失败、空数据、非法输入三种异常都有清晰的用户反馈，且自动化用例覆盖验证；② 数据驱动视图：搜索/筛选/增改全部只改内存数据再统一重渲染，逻辑清晰不易出 bug；③ 三维场景与主题深度结合而非摆设，并与图表配色体系呼应。")
p_h(n, "最大不足")
p_body(n, "① 添加/修改的自习室数据仅存于内存，刷新页面即丢失，未做持久化；② 表单校验依赖 Toast 弹窗，未定位到具体字段做行内提示；③ 三个页面头部导航与页脚为重复 HTML，未做模板化，维护时需多处同步修改。")

n = A["2. 局限性与改进"]
p_table(n, ["当前局限", "一周内的改进方案"], [
    ["自习室增改数据刷新后丢失", "用 localStorage 持久化自习室数组，提供“恢复初始数据”按钮"],
    ["表单错误提示不定位字段", "改为行内校验：错误字段红框＋下方提示文字，并加 aria 属性提升可访问性"],
    ["图表与查询相互独立", "实现联动：表格筛选后柱状图/饼图随过滤结果实时更新"],
    ["三维场景仅可观看", "为建筑绑定点击事件：点击弹出该楼栋食堂/自习室的实时数据卡片，与数据模块打通"],
    ["数据为静态模拟", "抽取数据访问层，便于后续替换为真实后端接口（fetch 同一 Promise 接口）"],
    ["重复的导航/页脚代码", "用 jQuery 动态注入公共头部/页脚，消除三处重复"],
], size=10.5, widths=[6.4, 8.4])

doc.save(OUT)
print("saved:", OUT)
print("images:", _img_seq[0])
