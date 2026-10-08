# Nav_Show 项目说明

## 项目定位

这是一个**纯渲染层 submodule**，职责是接收已计算好的数据，生成 HTML 业绩报告。

**不负责：**
- 数据获取（SQL/Excel/API）
- 指标计算（NavMetric）
- 数据清洗和对齐

**只负责：**
- 图表配置生成（pyecharts）
- HTML 渲染
- 前端交互逻辑

## 核心文件

### `performance_report.py`

- `ChartData`: TypedDict，定义图表数据结构
- `render_report()`: 唯一公开接口，接收数据 → 输出 HTML
- `_generate_chart_config()`: 内部函数，生成 ECharts 配置
- `__main__` 块：从 `test_data.json` 读取数据，生成两个示例 HTML（有/无基准）

### `templates/report.html`

单一模板，通过 CSS 控制有/无基准的布局差异：
- 有基准：三列指标（超额/策略/基准）
- 无基准：2×3 大卡片网格

### `assets/js/main.js`

前端逻辑：
- 图表高度自适应（根据容器宽度动态计算）
- 周期切换按钮绑定
- 有/无基准的 DOM 元素显示控制
- 数据填充（从 `window.reportData` 读取）

### `assets/css/style.css`

响应式样式：
- 桌面：4 列概览卡片，3 列指标
- 平板（≤1024px）：2 列概览卡片
- 手机（≤768px）：2 列概览卡片，单列指标，2 列无基准大卡片
- 手机（≤480px）：全单列

### `test_data.json`

持久化的测试数据，包含：
- `chartData`: 图表序列数据（日期、净值、回撤）
- `allData`: 各周期指标
- `hasBenchmark`: 是否有基准

**用途：** 在 `nav_interval_metric` 移除后，仍可通过 `python performance_report.py` 生成示例报告，用于 UI 调试。

## 母项目集成方式

```python
# 母项目负责数据获取和指标计算
from nav_interval_metric.nav_metric import NavMetric
from nav_show import render_report, ChartData

# 1. 获取原始数据（SQL/Excel/API）
nav_raw = get_nav_from_database(...)

# 2. 计算指标
nav_metric = NavMetric(name, nav, date, "W")
metrics = extract_metrics(nav_metric)  # 构造 metrics dict

# 3. 准备图表数据
chart_data = ChartData(
    dates=dates_str_list,
    nav=nav_pct_list,
    drawdown=drawdown_list,
    ...
)

# 4. 调用 submodule 生成 HTML
render_report(name, chart_data, metrics, "output.html", has_benchmark)
```

## 响应式设计要点

1. **图表高度自适应**：JS 根据容器宽度动态设置 `height`，避免 pyecharts 的固定 `700px`
2. **网格布局**：用 CSS Grid 而非 Flexbox，断点清晰
3. **无基准优化**：2×3 大卡片，数字更突出（28px），参考 Bloomberg Terminal 风格

## 已知问题

### 移动端显示异常（待修复）

目前手机端打开效果奇怪，需要进一步调试。

**可能原因：**
- pyecharts 生成的图表配置中 `width: "100%"` 在某些移动端容器内失效
- 概览卡片在极小屏幕（<360px）下布局未验证
- ECharts 的 `axisPointer` 和 `tooltip` 在触屏设备上交互体验差

**排查建议：**
1. Chrome DevTools → Toggle device toolbar，逐一测试 iPhone SE / iPhone 14 / iPad
2. 重点检查图表容器是否溢出（`overflow: hidden` 可能需要加到 `.chart-section`）
3. 触屏设备建议禁用 `axisPointer` 的 cross 模式，改为 `line`

## 开发建议

- 修改样式：编辑 `assets/css/style.css`
- 修改布局：编辑 `templates/report.html`
- 修改交互：编辑 `assets/js/main.js`
- 测试：运行 `python performance_report.py`，打开生成的 HTML

## 注意事项

- `test_data.json` 中的 `NaN` 会被转为 `null`（JSON 不支持 NaN）
- 图表配置中的日期格式必须是字符串（`"2023-01-01"`）
- 所有百分比数据在 Python 侧已转为小数（`0.37` = 37%），前端 `formatPercent` 会 `*100`
- 模板路径使用 `./assets/...`，不再需要 string-replace hack
