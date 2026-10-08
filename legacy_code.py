"""
Legacy Code - 数据准备和指标计算逻辑

这些代码已从 Nav_Show submodule 中移除，保留在此供母项目参考使用。
母项目应负责数据获取、清洗和指标计算，然后调用 Nav_Show 的 render_report() 生成 HTML。
"""

import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import Optional, Dict

# 需要从母项目导入
# from nav_interval_metric.nav_metric import NavMetric
# from nav_interval_metric.utils import generate_trading_date
# from nav_show import render_report, ChartData
# import pandas as pd


def prepare_data(
    date: NDArray[np.datetime64],
    nav: NDArray[np.floating],
    benchmark: Optional[NDArray[np.floating]] = None,
) -> pd.DataFrame:
    """
    准备数据：对齐日期，计算累计收益和回撤

    Args:
        date: 日期数组
        nav: 净值数组
        benchmark: 基准净值数组（可选）

    Returns:
        包含归一化净值、回撤等列的 DataFrame
    """
    assert len(date) == len(nav), "日期与净值数据长度不匹配"

    nav_norm = nav / nav[0]  # 归一化
    df = (
        pd.DataFrame({"date": pd.to_datetime(date), "nav": nav_norm})
        .set_index("date")
        .sort_index()
    )

    # 计算策略回撤
    cummax = np.maximum.accumulate(nav_norm)
    df["drawdown"] = (nav_norm - cummax) / cummax

    if benchmark is not None:
        assert len(date) == len(benchmark), "日期与基准数据长度不匹配"

        # 归一化基准
        df["benchmark"] = benchmark / benchmark[0]

        # 计算超额净值（几何超额）
        df["excess_nav"] = nav_norm / df["benchmark"].values

        # 计算基准回撤
        cummax_bench = np.maximum.accumulate(np.asarray(df["benchmark"].values))
        df["drawdown_benchmark"] = (df["benchmark"] - cummax_bench) / cummax_bench

        # 计算超额回撤
        cummax_excess = np.maximum.accumulate(np.asarray(df["excess_nav"].values))
        df["drawdown_excess"] = (df["excess_nav"] - cummax_excess) / cummax_excess

    return df


def calculate_indicators(
    name: str,
    date: NDArray[np.datetime64],
    nav_norm: NDArray[np.floating],
    benchmark_norm: Optional[NDArray[np.floating]] = None,
    excess_norm: Optional[NDArray[np.floating]] = None,
    last_date: Optional[np.datetime64] = None,
    last_week_date: Optional[np.datetime64] = None,
) -> Dict[str, dict]:
    """
    计算各周期指标

    Args:
        name: 产品名称
        date: 日期数组
        nav_norm: 归一化后的策略净值
        benchmark_norm: 归一化后的基准净值（可选）
        excess_norm: 归一化后的超额净值（可选）
        last_date: 最后日期（默认为 date[-1]）
        last_week_date: 上周最后日期（默认为 date[-2]）

    Returns:
        包含所有周期指标的字典，格式与 Nav_Show 的 metrics 参数一致
    """
    from nav_interval_metric.nav_metric import NavMetric

    assert date.dtype == np.dtype("datetime64[D]"), "日期必须是 datetime64[D] 类型"
    last_date = last_date if last_date is not None else date[-1]
    last_week_date = last_week_date if last_week_date is not None else date[-2]

    all_data = {}

    # 生成周期定义
    base_interval = NavMetric.generate_intervals(
        last_day=last_date, last_week_day=last_week_date
    )

    # 辅助函数：提取指标数据
    def _extract_metrics(metric: NavMetric, intervals: list, suffix: str = ""):
        data = {}
        # 区间指标
        data[f"interval{suffix}"] = {
            "start_date": np.datetime_as_string(metric.begin_date, unit="D"),
            "end_date": np.datetime_as_string(metric.end_date, unit="D"),
            "interval_return": metric.base_metric_dict["区间收益率"],
            "interval_anual_return": metric.base_metric_dict["年化收益率"],
            "interval_annual_vol": metric.base_metric_dict["年化波动率"],
            "interval_MDD": metric.base_metric_dict["最大回撤"],
            "interval_sharpe": metric.base_metric_dict["夏普比率"],
            "interval_karma": metric.base_metric_dict["卡玛比率"],
        }
        # 标准周期指标
        calculated_intervals = metric.calculate_interval_return(intervals)
        for _interval in calculated_intervals:
            data[_interval.name + suffix] = {
                "start_date": np.datetime_as_string(_interval.start_date, unit="D"),
                "end_date": np.datetime_as_string(_interval.end_date, unit="D"),
                "interval_return": _interval.interval_return,
                "interval_anual_return": _interval.interval_annual_return,
                "interval_annual_vol": _interval.interval_annual_vol,
                "interval_MDD": _interval.interval_MDD,
                "interval_sharpe": _interval.interval_sharpe,
                "interval_karma": _interval.interval_karma,
            }
        return data

    # 计算策略指标
    nav_metric = NavMetric(name, nav_norm.astype(np.float64), date, "W")
    all_data.update(_extract_metrics(nav_metric, base_interval))

    if benchmark_norm is not None and excess_norm is not None:
        # 计算基准指标
        benchmark_metric = NavMetric(
            f"{name}_Benchmark",
            benchmark_norm.astype(np.float64),
            date,
            "W",
        )
        all_data.update(_extract_metrics(benchmark_metric, base_interval, "_Benchmark"))

        # 计算超额收益指标
        excess_metric = NavMetric(
            f"{name}_Excess",
            excess_norm.astype(np.float64),
            date,
            "W",
        )
        all_data.update(_extract_metrics(excess_metric, base_interval, "_Excess"))

    return all_data


def prepare_chart_data_for_nav_show(df: pd.DataFrame, has_benchmark: bool) -> dict:
    """
    将 DataFrame 转换为 Nav_Show 的 ChartData 格式

    Args:
        df: prepare_data() 返回的 DataFrame
        has_benchmark: 是否有基准

    Returns:
        符合 ChartData TypedDict 的字典
    """
    dates = df.index.strftime("%Y-%m-%d").tolist()
    nav_pct = ((df["nav"].values - 1) * 100).round(2).tolist()
    drawdown = (df["drawdown"].values * 100).round(2).tolist()

    if has_benchmark:
        bench_pct = ((df["benchmark"].values - 1) * 100).round(2).tolist()
        excess_pct = ((df["excess_nav"].values - 1) * 100).round(2).tolist()
        drawdown_excess = (df["drawdown_excess"].values * 100).round(2).tolist()
    else:
        bench_pct = []
        excess_pct = []
        drawdown_excess = []

    return {
        "dates": dates,
        "nav": nav_pct,
        "drawdown": drawdown,
        "benchmark": bench_pct,
        "excess_nav": excess_pct,
        "drawdown_excess": drawdown_excess,
    }


# ============ 使用示例 ============

if __name__ == "__main__":
    """
    完整示例：从原始数据到生成 HTML 报告
    """
    # 1. 获取原始数据（示例：从 Excel 读取）

    df_raw = pd.read_excel("产品净值.xlsx")
    df_raw["日期"] = pd.to_datetime(df_raw["日期"])
    df_raw = df_raw.sort_values("日期").reset_index(drop=True)

    dates_raw = df_raw["日期"].values
    nav_raw = df_raw["复权净值"].values.astype(float)

    # 2. 对齐到周度交易日
    begin_date, end_date = dates_raw[0], dates_raw[-1]
    _, weekly_dates = generate_trading_date(
        begin_date - np.timedelta64(10, "D"),
        end_date + np.timedelta64(5, "D"),
    )
    nav_series = pd.Series(nav_raw, index=pd.to_datetime(dates_raw))
    nav_series = nav_series.reindex(weekly_dates).dropna()
    nav_series = nav_series[nav_series.index >= pd.to_datetime(begin_date)]

    date = nav_series.index.values
    nav = nav_series.values

    # 3. 准备数据（计算归一化、回撤等）
    df = prepare_data(date, nav, benchmark=None)

    # 4. 计算指标
    metrics = calculate_indicators(
        name="产品名称",
        date=date,
        nav_norm=df["nav"].values,
        benchmark_norm=None,
        excess_norm=None,
    )

    # 5. 准备图表数据
    chart_data = prepare_chart_data_for_nav_show(df, has_benchmark=False)

    # 6. 调用 Nav_Show 生成 HTML
    render_report(
        name="产品名称",
        chart_data=ChartData(**chart_data),
        metrics=metrics,
        output_html="report.html",
        has_benchmark=False,
    )
