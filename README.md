# Nav_Show

基金业绩报告生成器 - 纯渲染层 submodule

## 功能

接收已计算好的净值数据和指标，生成响应式 HTML 业绩报告。支持有/无基准两种模式。

## 安装

```bash
pip install pyecharts
```

## 使用

```python
from nav_show import render_report, ChartData

render_report(
    name="产品名称",
    chart_data=ChartData(
        dates=["2023-01-01", "2023-01-08", ...],  # ISO 日期字符串
        nav=[0.0, 1.2, 2.5, ...],                  # 归一化收益率（%）
        drawdown=[0.0, -0.5, -1.2, ...],           # 回撤（%）
        benchmark=[0.0, 0.8, 1.5, ...],            # 基准收益（可选）
        excess_nav=[0.0, 0.4, 1.0, ...],           # 超额收益（可选）
        drawdown_excess=[0.0, -0.2, -0.5, ...],    # 超额回撤（可选）
    ),
    metrics={
        "interval": {
            "start_date": "2023-01-01",
            "end_date": "2025-12-31",
            "interval_return": 1.37,
            "interval_anual_return": 0.46,
            "interval_annual_vol": 0.27,
            "interval_MDD": -0.25,
            "interval_sharpe": 1.63,
            "interval_karma": 1.86,
        },
        "ytd": {...},
        "recent_year": {...},
        # 有基准时需要 _Benchmark 和 _Excess 后缀的对应数据
    },
    output_html="report.html",
    has_benchmark=False,
)
```

## 数据格式

### ChartData

- `dates`: 日期列表（ISO 格式字符串）
- `nav`: 策略净值（归一化后的百分比，如 `[0.0, 1.2, 2.5]` 表示 0%, 1.2%, 2.5%）
- `drawdown`: 策略回撤（百分比）
- `benchmark`: 基准净值（可选，无基准时传空列表）
- `excess_nav`: 超额净值（可选）
- `drawdown_excess`: 超额回撤（可选）

### metrics

每个周期的指标字典，必须包含：
- `start_date`, `end_date`: 日期字符串
- `interval_return`: 区间收益率（小数，如 `0.37` 表示 37%）
- `interval_anual_return`: 年化收益率
- `interval_annual_vol`: 年化波动率
- `interval_MDD`: 最大回撤
- `interval_sharpe`: 夏普比率
- `interval_karma`: 卡玛比率

支持的周期：`interval`, `ytd`, `recent_year`, `recent_month`, `recent_week`, `y2024`, `y2023`, `y2022`

有基准时，每个周期需要三份数据：
- `{period}`: 策略
- `{period}_Benchmark`: 基准
- `{period}_Excess`: 超额

## 特性

- 📱 响应式设计，支持桌面/平板/手机
- 📊 ECharts 交互式图表，支持缩放、保存
- 🎨 无基准时自动切换为 2×3 大卡片布局
- 🔄 周期切换（今年以来/近一年/成立以来）
- 📦 零依赖（除 pyecharts），纯静态 HTML 输出

## 项目结构

```
Nav_Show/
├── __init__.py              # 公开接口
├── performance_report.py    # 核心渲染逻辑
├── templates/
│   └── report.html          # HTML 模板
├── assets/
│   ├── css/style.css        # 样式
│   └── js/main.js           # 前端逻辑
└── test_data.json           # 测试数据（供 UI 调试）
```

## 测试

```bash
python performance_report.py
```

生成 `index_with_benchmark.html` 和 `index_no_benchmark.html` 两个示例报告。

## License

MIT
