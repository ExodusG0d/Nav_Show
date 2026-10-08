import json
import shutil
from pathlib import Path
from typing import Optional, TypedDict
from pyecharts import options as opts
from pyecharts.charts import Line, Grid


class ChartData(TypedDict):
    dates: list
    nav: list
    drawdown: list
    benchmark: list  # 可选，无基准时传空列表
    excess_nav: list  # 可选，无基准时传空列表
    drawdown_excess: list  # 可选，无基准时传空列表


def _generate_chart_config(chart_data: ChartData, has_benchmark: bool) -> dict:
    date_list = chart_data["dates"]

    line = (
        Line(init_opts=opts.InitOpts(height="500px", theme="light"))
        .add_xaxis(date_list)
        .add_yaxis(
            "策略收益",
            chart_data["nav"],
            is_smooth=False,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2, color="#d9534f"),
        )
    )

    if has_benchmark:
        line.add_yaxis(
            "基准收益",
            chart_data["benchmark"],
            is_smooth=False,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2, color="#5cb85c"),
        ).add_yaxis(
            "超额收益",
            chart_data["excess_nav"],
            is_smooth=False,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1, color="#007bff"),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.2, color="#007bff"),
        )

    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title="收益回撤走势",
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=20, font_weight="bold", color="#333"
            ),
        ),
        legend_opts=opts.LegendOpts(pos_top="8%", pos_left="66%"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True, link=[{"xAxisIndex": "all"}]
        ),
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        yaxis_opts=opts.AxisOpts(
            name="收益率 (%)", axislabel_opts=opts.LabelOpts(formatter="{value} %")
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                type_="inside", xaxis_index=[0, 1], range_start=0, range_end=100
            )
        ],
        toolbox_opts=opts.ToolboxOpts(
            is_show=True,
            pos_left="right",
            feature=opts.ToolBoxFeatureOpts(
                save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                    title="保存为图片",
                    pixel_ratio=4,
                    background_color="white",
                    name="performance_report_chart",
                ),
                restore=True,
                magic_type=False,
                brush=False,
                data_view=False,
            ),
        ),
    )

    dd_chart = (
        Line()
        .add_xaxis(date_list)
        .add_yaxis(
            "策略回撤",
            chart_data["drawdown"],
            is_smooth=False,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1, color="#d9534f"),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5, color="#d9534f"),
        )
    )

    if has_benchmark:
        dd_chart.add_yaxis(
            "超额收益回撤",
            chart_data["drawdown_excess"],
            is_smooth=False,
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1, color="#5cb85c"),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5, color="#5cb85c"),
        )

    dd_chart.set_global_opts(
        yaxis_opts=opts.AxisOpts(
            name="回撤 (%)", axislabel_opts=opts.LabelOpts(formatter="{value} %")
        ),
        legend_opts=opts.LegendOpts(is_show=True, pos_left="66%", pos_top="66%"),
        xaxis_opts=opts.AxisOpts(is_show=False),
    )

    grid = Grid(init_opts=opts.InitOpts(width="100%", height="700px"))
    grid.add(line, grid_opts=opts.GridOpts(pos_top="12%", pos_bottom="38%"))
    grid.add(dd_chart, grid_opts=opts.GridOpts(pos_top="70%", pos_bottom="10%"))

    return json.loads(grid.dump_options_with_quotes())


def render_report(
    name: str,
    chart_data: ChartData,
    metrics: dict,
    output_html: str = "index.html",
    has_benchmark: bool = False,
):
    base_dir = Path(__file__).parent
    template_path = base_dir / "templates" / "report.html"

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件未找到: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace(
        "<h1>区间基础指标</h1>", f"<h1>{name} 业绩报告</h1>"
    )

    js_data = f"""
    window.reportData = {{
        version: "1.0",
        chartConfig: {json.dumps(_generate_chart_config(chart_data, has_benchmark))},
        allData: {json.dumps(metrics)},
        hasBenchmark: {str(has_benchmark).lower()}
    }};
    """

    html_content = html_content.replace(
        "<!-- DATA_INJECTION -->", f"<script>{js_data}</script>"
    )

    output_path = Path(output_html)
    output_dir = output_path.parent if output_path.parent != Path("") else Path(".")
    src_assets = base_dir / "assets"
    dest_assets = output_dir / "assets"
    if src_assets.exists() and output_dir.resolve() != Path(".").resolve():
        shutil.copytree(src_assets, dest_assets, dirs_exist_ok=True)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"业绩报告已生成: {output_html}")


if __name__ == "__main__":
    # 从 test_data.json 读取测试数据，生成两个版本的 HTML
    with open("test_data.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)

    chart_data_full = ChartData(**test_data["chartData"])
    metrics = test_data["allData"]

    # 生成有 benchmark 的版本
    render_report(
        name="乐水小波增强一号",
        chart_data=chart_data_full,
        metrics=metrics,
        output_html="index_with_benchmark.html",
        has_benchmark=True,
    )

    # 生成无 benchmark 的版本（只保留策略数据）
    chart_data_solo = ChartData(
        dates=chart_data_full["dates"],
        nav=chart_data_full["nav"],
        drawdown=chart_data_full["drawdown"],
        benchmark=[],
        excess_nav=[],
        drawdown_excess=[],
    )
    metrics_solo = {
        k: v for k, v in metrics.items() if "_Benchmark" not in k and "_Excess" not in k
    }

    render_report(
        name="乐水小波增强一号",
        chart_data=chart_data_solo,
        metrics=metrics_solo,
        output_html="index_no_benchmark.html",
        has_benchmark=False,
    )
