/* 通用工具函数 */
(function (global) {
  'use strict';

  /**
   * 加载本地 JSON 数据（带错误处理）
   * @param {string} url - JSON 文件路径
   * @returns {Promise<object>}
   */
  global.loadJSON = function (url) {
    return new Promise(function (resolve, reject) {
      $.getJSON(url)
        .done(function (data) {
          resolve(data);
        })
        .fail(function (jqxhr, textStatus, error) {
          var msg = '数据加载失败：' + (error || textStatus) + '。请检查 JSON 文件路径或启动本地服务器后重试。';
          showToast(msg, 'danger');
          reject(new Error(msg));
        });
    });
  };

  /**
   * 显示 Toast 提示
   * @param {string} message
   * @param {string} type - success / danger / warning / info
   */
  global.showToast = function (message, type) {
    type = type || 'info';
    var colors = {
      success: '#16a34a',
      danger: '#dc2626',
      warning: '#f59e0b',
      info: '#2563eb'
    };
    var $toast = $('<div>')
      .css({
        background: colors[type] || colors.info,
        color: '#fff',
        padding: '12px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        marginBottom: '10px',
        fontSize: '14px',
        maxWidth: '360px',
        animation: 'slideIn 0.3s ease'
      })
      .text(message);

    if (!$('.toast-container').length) {
      $('<div class="toast-container"></div>').appendTo('body');
    }
    $('.toast-container').append($toast);

    setTimeout(function () {
      $toast.fadeOut(300, function () { $(this).remove(); });
    }, 3000);
  };

  // 注入动画
  if (!$('#toast-style').length) {
    $('<style id="toast-style">@keyframes slideIn{from{opacity:0;transform:translateX(100%)}to{opacity:1;transform:translateX(0)}}</style>').appendTo('head');
  }

  /**
   * 数字格式化（千分位）
   */
  global.formatNumber = function (num) {
    if (num == null) return '-';
    return Number(num).toLocaleString('zh-CN');
  };

  /**
   * 渲染星级评分
   */
  global.renderStars = function (rating) {
    var full = Math.floor(rating);
    var half = rating - full >= 0.5;
    var html = '';
    for (var i = 0; i < full; i++) html += '<i class="bi bi-star-fill text-warning"></i>';
    if (half) html += '<i class="bi bi-star-half text-warning"></i>';
    var empty = 5 - full - (half ? 1 : 0);
    for (var j = 0; j < empty; j++) html += '<i class="bi bi-star text-warning"></i>';
    return html + ' <span class="text-muted small">' + rating.toFixed(1) + '</span>';
  };

  /**
   * 获取可坐状态徽章
   */
  global.getSeatBadge = function (available, capacity) {
    if (available === 0) return '<span class="badge badge-full">已满</span>';
    var rate = available / capacity;
    if (rate < 0.2) return '<span class="badge badge-warning">紧张</span>';
    return '<span class="badge badge-available">充足</span>';
  };
})(window);
