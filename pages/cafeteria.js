/* 食堂数据展示页面脚本 */
$(function () {
  'use strict';

  var cafeData = null;
  var canteenMap = {};

  loadJSON('../data/cafeteria.json').then(function (data) {
    cafeData = data;
    data.canteens.forEach(function (c) { canteenMap[c.id] = c.name; });
    initCanteenFilter(data.canteens);
    renderCanteens(data.canteens);
    renderDishes(data.dishes);
    renderSalesChart(data.dishes);
    renderCategoryChart(data.categorySales);
  }).catch(function () { /* 错误已在 loadJSON 处理 */ });

  // 食堂筛选下拉
  function initCanteenFilter(canteens) {
    var $sel = $('#filter-canteen');
    canteens.forEach(function (c) {
      $sel.append('<option value="' + c.id + '">' + c.name + '</option>');
    });
  }

  // 渲染食堂卡片
  function renderCanteens(canteens) {
    var $list = $('#canteen-list').empty();
    canteens.forEach(function (c) {
      var popularBadge = c.popular ? '<span class="badge bg-danger ms-2"><i class="bi bi-fire"></i> 热门</span>' : '';
      var html =
        '<div class="col-sm-6 col-lg-4">' +
          '<div class="stat-card">' +
            '<div class="d-flex justify-content-between align-items-start mb-2">' +
              '<h5 class="mb-0">' + c.name + popularBadge + '</h5>' +
              '<span class="badge bg-primary">' + c.location + '</span>' +
            '</div>' +
            '<p class="text-muted small mb-2"><i class="bi bi-clock"></i> ' + c.openTime + '</p>' +
            '<div class="d-flex justify-content-between text-center mt-3">' +
              '<div><div class="fs-5 fw-bold text-primary">' + c.floors + '</div><small class="text-muted">楼层</small></div>' +
              '<div><div class="fs-5 fw-bold text-success">' + formatNumber(c.seats) + '</div><small class="text-muted">座位</small></div>' +
              '<div><div>' + renderStars(c.rating) + '</div><small class="text-muted">评分</small></div>' +
            '</div>' +
          '</div>' +
        '</div>';
      $list.append(html);
    });
  }

  // 渲染菜品表格（支持搜索筛选）
  function renderDishes(dishes) {
    var keyword = $('#search-input').val().trim().toLowerCase();
    var category = $('#filter-category').val();
    var canteenId = $('#filter-canteen').val();

    var filtered = dishes.filter(function (d) {
      var matchKeyword = !keyword || d.name.toLowerCase().indexOf(keyword) !== -1;
      var matchCategory = !category || d.category === category;
      var matchCanteen = !canteenId || String(d.canteenId) === String(canteenId);
      return matchKeyword && matchCategory && matchCanteen;
    });

    var $tbody = $('#dish-tbody').empty();
    if (filtered.length === 0) {
      $('#dish-empty').show();
      return;
    }
    $('#dish-empty').hide();

    filtered.forEach(function (d) {
      var tr =
        '<tr>' +
          '<td><strong>' + d.name + '</strong></td>' +
          '<td><span class="badge bg-light text-dark">' + d.category + '</span></td>' +
          '<td>¥' + d.price + '</td>' +
          '<td>' + renderStars(d.rating) + '</td>' +
          '<td>' + formatNumber(d.sales) + '</td>' +
          '<td>' + canteenMap[d.canteenId] + '</td>' +
        '</tr>';
      $tbody.append(tr);
    });
  }

  // 菜品销量 TOP8 柱状图
  function renderSalesChart(dishes) {
    var top = dishes.slice().sort(function (a, b) { return b.sales - a.sales; }).slice(0, 8);
    var chart = echarts.init(document.getElementById('chart-sales'));
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: top.map(function (d) { return d.name; }), axisLabel: { rotate: 20 } },
      yAxis: { type: 'value', name: '销量' },
      series: [{
        type: 'bar',
        data: top.map(function (d) { return d.sales; }),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#60a5fa' },
            { offset: 1, color: '#2563eb' }
          ]),
          borderRadius: [6, 6, 0, 0]
        },
        label: { show: true, position: 'top' }
      }]
    });
    $(window).on('resize', function () { chart.resize(); });
  }

  // 分类饼图
  function renderCategoryChart(categorySales) {
    var chart = echarts.init(document.getElementById('chart-category'));
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['38%', '62%'],
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: categorySales,
        color: ['#60a5fa', '#34d399', '#fbbf24', '#f472b6', '#a78bfa']
      }]
    });
    $(window).on('resize', function () { chart.resize(); });
  }

  // 事件绑定
  $('#search-input').on('input', function () {
    if (cafeData) renderDishes(cafeData.dishes);
  });
  $('#filter-category, #filter-canteen').on('change', function () {
    if (cafeData) renderDishes(cafeData.dishes);
  });
  $('#btn-reset').on('click', function () {
    $('#search-input').val('');
    $('#filter-category').val('');
    $('#filter-canteen').val('');
    if (cafeData) renderDishes(cafeData.dishes);
    showToast('筛选条件已重置', 'info');
  });
});
