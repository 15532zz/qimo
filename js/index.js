/* 首页脚本 */
$(function () {
  'use strict';

  // 并行加载两个 JSON 数据
  Promise.all([
    loadJSON('data/cafeteria.json'),
    loadJSON('data/studyroom.json')
  ]).then(function (results) {
    var cafe = results[0];
    var study = results[1];

    renderStats(cafe, study);
    renderFlowChart(cafe);
    renderPieChart(cafe);

    // 初始化 3D 场景
    initCampusScene('three-container');
  }).catch(function (err) {
    console.error(err);
    $('#stat-canteens, #stat-dishes, #stat-rooms, #stat-seats').text('加载失败');
  });

  // 渲染统计卡片
  function renderStats(cafe, study) {
    $('#stat-canteens').text(cafe.canteens.length);
    $('#stat-dishes').text(cafe.dishes.length);
    $('#stat-rooms').text(study.rooms.length);

    var totalAvailable = 0;
    study.rooms.forEach(function (r) { totalAvailable += r.available; });
    $('#stat-seats').text(formatNumber(totalAvailable));
  }

  // 分时人流折线图
  function renderFlowChart(cafe) {
    var chart = echarts.init(document.getElementById('chart-flow'));
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['第一食堂', '第二食堂', '第三食堂'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: cafe.hourlyFlow.hours
      },
      yAxis: { type: 'value', name: '人次' },
      series: [
        {
          name: '第一食堂', type: 'line', smooth: true,
          data: cafe.hourlyFlow.first,
          itemStyle: { color: '#60a5fa' },
          areaStyle: { opacity: 0.2 }
        },
        {
          name: '第二食堂', type: 'line', smooth: true,
          data: cafe.hourlyFlow.second,
          itemStyle: { color: '#f472b6' },
          areaStyle: { opacity: 0.2 }
        },
        {
          name: '第三食堂', type: 'line', smooth: true,
          data: cafe.hourlyFlow.third,
          itemStyle: { color: '#34d399' },
          areaStyle: { opacity: 0.2 }
        }
      ]
    });
    $(window).on('resize', function () { chart.resize(); });
  }

  // 菜品分类饼图
  function renderPieChart(cafe) {
    var chart = echarts.init(document.getElementById('chart-pie'));
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        avoidLabelOverlap: true,
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: cafe.categorySales,
        color: ['#60a5fa', '#34d399', '#fbbf24', '#f472b6', '#a78bfa']
      }]
    });
    $(window).on('resize', function () { chart.resize(); });
  }
});
