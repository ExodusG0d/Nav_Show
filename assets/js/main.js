document.addEventListener('DOMContentLoaded', () => {
    if (!window.reportData) {
        console.error("未找到报告数据");
        return;
    }

    const { chartConfig, allData, hasBenchmark } = window.reportData;

    // 图表高度自适应
    const chartContainer = document.getElementById('chart-container');
    const setChartHeight = () => {
        const width = chartContainer.offsetWidth;
        chartContainer.style.height = Math.max(Math.min(width * 0.6, 700), 400) + 'px';
    };
    setChartHeight();
    window.addEventListener('resize', () => {
        setChartHeight();
        myChart.resize();
    });

    const myChart = echarts.init(chartContainer);
    myChart.setOption(chartConfig);

    // 控制 benchmark 相关元素显示
    if (!hasBenchmark) {
        document.querySelectorAll('.benchmark-item').forEach(el => el.style.display = 'none');
        document.querySelector('.indicators-grid').style.display = 'none';
        document.querySelector('.indicators-grid-solo').style.display = 'grid';
    }

    const el = (id) => document.getElementById(id);
    const formatPercent = (val) => (val != null) ? (val * 100).toFixed(2) + '%' : '--';
    const formatNumber = (val) => (val != null) ? val.toFixed(2) : '--';
    const formatDate = (s) => s ? s.split(' ')[0] : '--';

    const populateSummaryCards = () => {
        ['recent_week', 'recent_month', 'ytd', 'recent_year', 'interval'].forEach(period => {
            const sData = allData[period];
            if (!sData) return;

            const dateEl = el(`summary-date-${period}`);
            if (dateEl) dateEl.innerText = `${formatDate(sData.start_date)} ~ ${formatDate(sData.end_date)}`;

            const sEl = el(`summary-strategy-${period}`);
            if (sEl) sEl.innerText = formatPercent(sData.interval_return);

            if (hasBenchmark) {
                const bData = allData[`${period}_Benchmark`];
                const eData = allData[`${period}_Excess`];
                const bEl = el(`summary-benchmark-${period}`);
                const eEl = el(`summary-excess-${period}`);
                if (bEl && bData) bEl.innerText = formatPercent(bData.interval_return);
                if (eEl && eData) eEl.innerText = formatPercent(eData.interval_return);
            }
        });
    };

    const updateIndicators = (period) => {
        const sData = allData[period];
        if (!sData) { console.warn(`未找到周期 ${period} 的数据`); return; }

        const rangeEl = el('indicator-date-range');
        if (rangeEl) rangeEl.innerText = `(${formatDate(sData.start_date)} ~ ${formatDate(sData.end_date)})`;

        if (hasBenchmark) {
            // 三列布局
            el('ind-return-strategy').innerText = formatPercent(sData.interval_return);
            el('ind-annual-return-strategy').innerText = formatPercent(sData.interval_anual_return);
            el('ind-annual-vol-strategy').innerText = formatPercent(sData.interval_annual_vol);
            el('ind-mdd-strategy').innerText = formatPercent(sData.interval_MDD);
            el('ind-sharpe-strategy').innerText = formatNumber(sData.interval_sharpe);
            el('ind-karma-strategy').innerText = formatNumber(sData.interval_karma);

            const bData = allData[`${period}_Benchmark`];
            const eData = allData[`${period}_Excess`];
            if (bData) {
                el('ind-return-benchmark').innerText = formatPercent(bData.interval_return);
                el('ind-annual-return-benchmark').innerText = formatPercent(bData.interval_anual_return);
                el('ind-annual-vol-benchmark').innerText = formatPercent(bData.interval_annual_vol);
                el('ind-mdd-benchmark').innerText = formatPercent(bData.interval_MDD);
                el('ind-sharpe-benchmark').innerText = formatNumber(bData.interval_sharpe);
                el('ind-karma-benchmark').innerText = formatNumber(bData.interval_karma);
            }
            if (eData) {
                el('ind-return-excess').innerText = formatPercent(eData.interval_return);
                el('ind-annual-return-excess').innerText = formatPercent(eData.interval_anual_return);
                el('ind-annual-vol-excess').innerText = formatPercent(eData.interval_annual_vol);
                el('ind-mdd-excess').innerText = formatPercent(eData.interval_MDD);
                el('ind-sharpe-excess').innerText = formatNumber(eData.interval_sharpe);
                el('ind-karma-excess').innerText = formatNumber(eData.interval_karma);
            }
        } else {
            // 2×3 大卡片
            el('solo-return').innerText = formatPercent(sData.interval_return);
            el('solo-annual-return').innerText = formatPercent(sData.interval_anual_return);
            el('solo-annual-vol').innerText = formatPercent(sData.interval_annual_vol);
            el('solo-mdd').innerText = formatPercent(sData.interval_MDD);
            el('solo-sharpe').innerText = formatNumber(sData.interval_sharpe);
            el('solo-karma').innerText = formatNumber(sData.interval_karma);
        }
    };

    const buttons = document.querySelectorAll('.period-btn');
    buttons.forEach(button => {
        button.addEventListener('click', (event) => {
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            updateIndicators(event.target.dataset.period);
        });
    });

    populateSummaryCards();
    updateIndicators('interval');
});
