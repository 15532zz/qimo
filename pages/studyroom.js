/* 自习室管理页面脚本 */
$(function () {
  'use strict';

  var studyData = null;
  var rooms = [];

  loadJSON('../data/studyroom.json').then(function (data) {
    studyData = data;
    rooms = JSON.parse(JSON.stringify(data.rooms)); // 深拷贝，便于增删改
    renderStats();
    renderRooms();
    renderTrendChart(data.usageTrend);
    renderBuildingChart(data.buildingStats);
  }).catch(function () { /* 错误已处理 */ });

  // 统计
  function renderStats() {
    var totalCap = 0, totalAvail = 0;
    rooms.forEach(function (r) {
      totalCap += r.capacity;
      totalAvail += r.available;
    });
    $('#stat-rooms').text(rooms.length);
    $('#stat-capacity').text(formatNumber(totalCap));
    $('#stat-available').text(formatNumber(totalAvail));
    var rate = totalCap ? Math.round((1 - totalAvail / totalCap) * 100) : 0;
    $('#stat-rate').text(rate + '%');
  }

  // 渲染表格
  function renderRooms() {
    var keyword = $('#search-input').val().trim().toLowerCase();
    var availFilter = $('#filter-available').val();

    var filtered = rooms.filter(function (r) {
      var matchKw = !keyword ||
        r.name.toLowerCase().indexOf(keyword) !== -1 ||
        r.location.toLowerCase().indexOf(keyword) !== -1;
      var matchAvail = !availFilter ||
        (availFilter === 'available' && r.available > 0) ||
        (availFilter === 'full' && r.available === 0);
      return matchKw && matchAvail;
    });

    var $tbody = $('#room-tbody').empty();
    if (filtered.length === 0) {
      $('#room-empty').show();
      return;
    }
    $('#room-empty').hide();

    filtered.forEach(function (r) {
      var facilities = '';
      if (r.hasPower) facilities += '<i class="bi bi-plug-fill text-primary me-1" title="有电源"></i>';
      if (r.hasWifi) facilities += '<i class="bi bi-wifi text-success" title="有WiFi"></i>';
      if (!facilities) facilities = '<span class="text-muted small">无</span>';

      var tr =
        '<tr>' +
          '<td><strong>' + r.name + '</strong></td>' +
          '<td>' + r.location + '</td>' +
          '<td>' + r.capacity + '</td>' +
          '<td class="fw-bold ' + (r.available > 0 ? 'text-success' : 'text-danger') + '">' + r.available + '</td>' +
          '<td>' + getSeatBadge(r.available, r.capacity) + '</td>' +
          '<td><small class="text-muted">' + (r.openTime || '-') + '</small></td>' +
          '<td>' + facilities + '</td>' +
          '<td>' +
            '<button class="btn btn-sm btn-outline-primary me-1 btn-edit" data-id="' + r.id + '">' +
              '<i class="bi bi-pencil"></i> 修改' +
            '</button>' +
          '</td>' +
        '</tr>';
      $tbody.append(tr);
    });
  }

  // 使用率趋势图
  function renderTrendChart(trend) {
    var chart = echarts.init(document.getElementById('chart-trend'));
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['上午', '下午', '晚上'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: trend.days },
      yAxis: { type: 'value', name: '使用率(%)', max: 100 },
      series: [
        { name: '上午', type: 'line', smooth: true, data: trend.morning, itemStyle: { color: '#fbbf24' }, areaStyle: { opacity: 0.15 } },
        { name: '下午', type: 'line', smooth: true, data: trend.afternoon, itemStyle: { color: '#60a5fa' }, areaStyle: { opacity: 0.15 } },
        { name: '晚上', type: 'line', smooth: true, data: trend.evening, itemStyle: { color: '#f472b6' }, areaStyle: { opacity: 0.15 } }
      ]
    });
    $(window).on('resize', function () { chart.resize(); });
  }

  // 楼栋座位柱状图
  function renderBuildingChart(buildingStats) {
    var chart = echarts.init(document.getElementById('chart-building'));
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value', name: '座位数' },
      yAxis: { type: 'category', data: buildingStats.map(function (b) { return b.building; }) },
      series: [{
        type: 'bar',
        data: buildingStats.map(function (b) { return b.totalSeats; }),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#34d399' },
            { offset: 1, color: '#059669' }
          ]),
          borderRadius: [0, 6, 6, 0]
        },
        label: { show: true, position: 'right' }
      }]
    });
    $(window).on('resize', function () { chart.resize(); });
  }

  // ===== 模态框操作 =====
  var modalEl = document.getElementById('room-modal');
  var bsModal = new bootstrap.Modal(modalEl);

  // 打开添加
  $('#btn-add').on('click', function () {
    $('#modal-title').html('<i class="bi bi-plus-lg"></i> 添加自习室');
    $('#room-form')[0].reset();
    $('#room-id').val('');
    bsModal.show();
  });

  // 打开编辑
  $(document).on('click', '.btn-edit', function () {
    var id = parseInt($(this).data('id'));
    var room = rooms.find(function (r) { return r.id === id; });
    if (!room) return;
    $('#modal-title').html('<i class="bi bi-pencil"></i> 修改自习室');
    $('#room-id').val(room.id);
    $('#room-name').val(room.name);
    $('#room-location').val(room.location);
    $('#room-capacity').val(room.capacity);
    $('#room-available').val(room.available);
    $('#room-opentime').val(room.openTime || '');
    $('#room-power').prop('checked', !!room.hasPower);
    $('#room-wifi').prop('checked', !!room.hasWifi);
    bsModal.show();
  });

  // 保存
  $('#btn-save').on('click', function () {
    var name = $('#room-name').val().trim();
    var location = $('#room-location').val().trim();
    var capacity = parseInt($('#room-capacity').val());
    var available = parseInt($('#room-available').val());

    // 校验
    if (!name || !location || isNaN(capacity) || isNaN(available)) {
      showToast('请完整填写名称、位置、容量和可用座位', 'danger');
      return;
    }
    if (capacity < 1) { showToast('容量必须大于 0', 'danger'); return; }
    if (available < 0) { showToast('可用座位不能为负数', 'danger'); return; }
    if (available > capacity) { showToast('可用座位不能大于总容量', 'danger'); return; }

    var id = $('#room-id').val();
    var record = {
      name: name,
      location: location,
      capacity: capacity,
      available: available,
      openTime: $('#room-opentime').val().trim() || '08:00-21:00',
      hasPower: $('#room-power').is(':checked'),
      hasWifi: $('#room-wifi').is(':checked')
    };

    if (id) {
      // 修改
      var idx = rooms.findIndex(function (r) { return r.id === parseInt(id); });
      if (idx !== -1) {
        rooms[idx] = $.extend({}, rooms[idx], record);
        showToast('修改成功', 'success');
      }
    } else {
      // 添加
      var newId = rooms.length ? Math.max.apply(null, rooms.map(function (r) { return r.id; })) + 1 : 1;
      record.id = newId;
      rooms.push(record);
      showToast('添加成功', 'success');
    }

    bsModal.hide();
    renderStats();
    renderRooms();
  });

  // 搜索/筛选事件
  $('#search-input').on('input', renderRooms);
  $('#filter-available').on('change', renderRooms);
});
