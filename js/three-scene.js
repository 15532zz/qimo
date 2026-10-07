/* Three.js 三维展示 - 校园建筑场景 */
(function (global) {
  'use strict';

  /**
   * 初始化 Three.js 校园三维场景
   * @param {string} containerId - 容器 DOM id
   */
  global.initCampusScene = function (containerId) {
    var container = document.getElementById(containerId);
    if (!container) return null;

    // 加载中提示
    var $loading = $('<div class="three-loading"><div class="spinner-border text-primary" role="status"></div><div class="mt-2 small">正在加载三维场景...</div></div>');
    $(container).append($loading);

    try {
      // 场景
      var scene = new THREE.Scene();
      scene.background = new THREE.Color(0xe0f2fe);
      scene.fog = new THREE.Fog(0xe0f2fe, 30, 80);

      // 相机
      var width = container.clientWidth;
      var height = container.clientHeight;
      var camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
      camera.position.set(18, 16, 22);
      camera.lookAt(0, 0, 0);

      // 渲染器
      var renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.shadowMap.enabled = true;
      container.appendChild(renderer.domElement);

      // 光照
      var ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);

      var dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
      dirLight.position.set(15, 20, 10);
      dirLight.castShadow = true;
      dirLight.shadow.mapSize.set(1024, 1024);
      scene.add(dirLight);

      // 地面（草坪）
      var groundGeo = new THREE.PlaneGeometry(60, 60);
      var groundMat = new THREE.MeshLambertMaterial({ color: 0x86efac });
      var ground = new THREE.Mesh(groundGeo, groundMat);
      ground.rotation.x = -Math.PI / 2;
      ground.receiveShadow = true;
      scene.add(ground);

      // 道路
      var roadMat = new THREE.MeshLambertMaterial({ color: 0xcbd5e1 });
      var road1 = new THREE.Mesh(new THREE.PlaneGeometry(60, 3), roadMat);
      road1.rotation.x = -Math.PI / 2;
      road1.position.y = 0.01;
      scene.add(road1);

      var road2 = new THREE.Mesh(new THREE.PlaneGeometry(3, 60), roadMat);
      road2.rotation.x = -Math.PI / 2;
      road2.position.y = 0.01;
      scene.add(road2);

      // 创建建筑函数
      function createBuilding(x, z, w, h, d, color, label) {
        var group = new THREE.Group();

        // 楼体
        var bodyGeo = new THREE.BoxGeometry(w, h, d);
        var bodyMat = new THREE.MeshLambertMaterial({ color: color });
        var body = new THREE.Mesh(bodyGeo, bodyMat);
        body.position.y = h / 2;
        body.castShadow = true;
        body.receiveShadow = true;
        group.add(body);

        // 屋顶
        var roofGeo = new THREE.BoxGeometry(w + 0.4, 0.5, d + 0.4);
        var roofMat = new THREE.MeshLambertMaterial({ color: 0x475569 });
        var roof = new THREE.Mesh(roofGeo, roofMat);
        roof.position.y = h + 0.25;
        roof.castShadow = true;
        group.add(roof);

        // 窗户
        var windowMat = new THREE.MeshLambertMaterial({ color: 0x7dd3fc });
        var winGeo = new THREE.PlaneGeometry(0.6, 0.6);
        var floors = Math.floor(h / 2);
        var cols = Math.floor(w / 1.5);
        for (var f = 0; f < floors; f++) {
          for (var c = 0; c < cols; c++) {
            var winFront = new THREE.Mesh(winGeo, windowMat);
            winFront.position.set(-w / 2 + 1 + c * 1.5, 1.2 + f * 2, d / 2 + 0.01);
            group.add(winFront);

            var winBack = new THREE.Mesh(winGeo, windowMat);
            winBack.position.set(-w / 2 + 1 + c * 1.5, 1.2 + f * 2, -d / 2 - 0.01);
            winBack.rotation.y = Math.PI;
            group.add(winBack);
          }
        }

        group.position.set(x, 0, z);
        group.userData = { label: label };
        return group;
      }

      // 建筑数据
      var buildings = [
        { x: -10, z: -8, w: 5, h: 8, d: 4, color: 0x60a5fa, label: '图书馆' },
        { x: 10, z: -8, w: 6, h: 10, d: 5, color: 0xf472b6, label: '第二食堂' },
        { x: -10, z: 10, w: 4, h: 6, d: 4, color: 0x34d399, label: '教学楼A' },
        { x: 10, z: 10, w: 4, h: 7, d: 4, color: 0xfbbf24, label: '教学楼B' },
        { x: 0, z: -14, w: 5, h: 9, d: 4, color: 0xa78bfa, label: '信息楼' },
        { x: 0, z: 14, w: 4, h: 5, d: 4, color: 0xfb7185, label: '体育馆' }
      ];

      var buildingGroup = new THREE.Group();
      buildings.forEach(function (b) {
        buildingGroup.add(createBuilding(b.x, b.z, b.w, b.h, b.d, b.color, b.label));
      });
      scene.add(buildingGroup);

      // 树木
      function createTree(x, z) {
        var tree = new THREE.Group();
        var trunkGeo = new THREE.CylinderGeometry(0.2, 0.3, 1.5, 8);
        var trunkMat = new THREE.MeshLambertMaterial({ color: 0x92400e });
        var trunk = new THREE.Mesh(trunkGeo, trunkMat);
        trunk.position.y = 0.75;
        trunk.castShadow = true;
        tree.add(trunk);

        var leavesGeo = new THREE.ConeGeometry(1.2, 2.5, 8);
        var leavesMat = new THREE.MeshLambertMaterial({ color: 0x16a34a });
        var leaves = new THREE.Mesh(leavesGeo, leavesMat);
        leaves.position.y = 2.5;
        leaves.castShadow = true;
        tree.add(leaves);

        tree.position.set(x, 0, z);
        return tree;
      }

      var treePositions = [
        [-6, -6], [6, -6], [-6, 6], [6, 6],
        [-14, 0], [14, 0], [0, -6], [0, 6],
        [-3, -3], [3, 3], [-12, -12], [12, 12]
      ];
      treePositions.forEach(function (p) {
        scene.add(createTree(p[0], p[1]));
      });

      // 轨道控制器
      if (global.OrbitControls) {
        var controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 50;
        controls.maxPolarAngle = Math.PI / 2.2;
      }

      $loading.remove();

      // 动画循环
      var animId = null;
      function animate() {
        animId = requestAnimationFrame(animate);
        if (controls) controls.update();
        renderer.render(scene, camera);
      }
      animate();

      // 窗口缩放
      function onResize() {
        var w = container.clientWidth;
        var h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      }
      window.addEventListener('resize', onResize);

      // 返回清理函数
      return {
        dispose: function () {
          if (animId) cancelAnimationFrame(animId);
          window.removeEventListener('resize', onResize);
          renderer.dispose();
          if (container.contains(renderer.domElement)) {
            container.removeChild(renderer.domElement);
          }
        }
      };
    } catch (e) {
      $loading.remove();
      $(container).html('<div class="three-loading text-danger"><i class="bi bi-exclamation-triangle"></i> 三维场景加载失败：' + e.message + '</div>');
      console.error('Three.js init error:', e);
      return null;
    }
  };
})(window);
