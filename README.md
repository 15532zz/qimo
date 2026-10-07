# 校园生活服务数据中心

> 期末大作业：信息与数据展示中心响应式前端应用

## 一、项目简介

本项目是一个面向校园生活服务的信息与数据展示中心，涵盖**食堂数据展示**与**自习室管理**两大功能模块，包含首页概览、数据图表、三维校园场景等内容。支持桌面端与移动端响应式布局。

## 二、技术栈

| 类别 | 技术 |
|------|------|
| 布局框架 | Bootstrap 5 |
| DOM 操作 | jQuery 3.7 |
| 图表库 | ECharts 5.4 |
| 三维引擎 | Three.js 0.160（含 OrbitControls） |
| 数据来源 | 本地 JSON 文件 |
| 其他 | Bootstrap Icons |

> 全部使用课堂讲授的前端技术，无后端服务器，未使用 React / Vue 等框架。

## 三、目录结构

```
qimodazuoyei/
├── index.html              # 首页（概览 + 图表 + 3D场景）
├── pages/
│   ├── cafeteria.html      # 食堂数据展示页
│   └── studyroom.html      # 自习室管理页
├── data/
│   ├── cafeteria.json      # 食堂与菜品数据
│   └── studyroom.json      # 自习室数据
├── css/
│   └── style.css           # 全局样式
├── js/
│   ├── common.js           # 通用工具（JSON加载、Toast提示、星级渲染）
│   ├── index.js            # 首页逻辑
│   └── three-scene.js      # Three.js 三维校园场景
├── pages/
│   ├── cafeteria.js        # 食堂页逻辑
│   └── studyroom.js        # 自习室页逻辑
└── README.md               # 本说明文件
```

## 四、功能说明

### 1. 首页（index.html）
- 食堂/菜品/自习室/可用座位 **4 项数据概览卡片**
- **分时人流趋势折线图**（三个食堂对比）
- **菜品分类销量饼图**
- **三维校园建筑场景**（Three.js，可拖拽旋转、滚轮缩放）

### 2. 食堂数据展示（pages/cafeteria.html）
- 食堂概览卡片（楼层、座位、评分、热门标记）
- **菜品查询**：支持按名称搜索、按分类/食堂筛选
- 菜品销量 **TOP8 柱状图**
- 分类销量 **饼图**

### 3. 自习室管理（pages/studyroom.html）
- 4 项统计：自习室数、总座位、可用座位、平均使用率
- **查询**：按名称/位置搜索、按可用状态筛选
- **添加自习室**（弹出模态框表单，含字段校验）
- **修改自习室**（编辑已有记录）
- 一周使用率趋势图、各楼栋座位分布柱状图

## 五、运行方式

由于项目通过 `$.getJSON` 加载本地 JSON 文件，**不能直接双击 HTML 文件运行**（浏览器 file:// 协议会限制 AJAX 请求），需要通过本地服务器访问。

### 方式一：Python 内置服务器（推荐）

在项目根目录下执行：

```bash
# Python 3
python -m http.server 8080
```

然后浏览器访问：`http://localhost:8080/`

### 方式二：VS Code Live Server 插件

在 VS Code 中安装 **Live Server** 插件，右键 `index.html` → "Open with Live Server"。

### 方式三：Node.js http-server

```bash
npx http-server -p 8080
```

然后访问 `http://localhost:8080/`。

## 六、错误提示说明

- 若 JSON 数据加载失败，页面右上角会弹出红色 Toast 提示，并在控制台输出错误信息。
- 自习室添加/修改时，对必填项、容量、可用座位范围进行校验，不符合规则时弹出提示。
- 三维场景加载失败时，在场景区域内显示错误提示，不影响其他功能。

## 七、响应式适配

- 使用 Bootstrap 栅格系统，在手机端自动切换为单列布局。
- 图表容器、3D 场景高度在小屏设备上自动缩小。
- 导航栏在移动端折叠为汉堡菜单。
