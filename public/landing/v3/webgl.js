/**
 * Landing Page V3 - WebGL Module
 * 3D logo animation and particle effects (optional, feature-flagged)
 */

export default {
  config: null,
  features: null,
  scene: null,
  camera: null,
  renderer: null,
  logoMesh: null,

  async init(config, features) {
    this.config = config;
    this.features = features;

    // Only initialize if WebGL is supported and enabled
    if (!features.webgl || !config.features.webgl) {
      return;
    }

    // Load Three.js if not already loaded
    if (typeof THREE === 'undefined') {
      try {
        await window.LandingV3Utils.loadScript('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js');
      } catch (error) {
        window.LandingV3Utils?.logError('Failed to load Three.js', error);
        return;
      }
    }

    // Initialize WebGL scene
    this.initScene();
  },

  initScene() {
    try {
      const container = document.querySelector('[data-v3="webgl-container"]');
      if (!container) {
        // Create container if it doesn't exist
        const hero = document.querySelector('.hero[data-v3="hero"]');
        if (hero) {
          const canvas = document.createElement('canvas');
          canvas.setAttribute('data-v3', 'webgl-container');
          canvas.style.position = 'absolute';
          canvas.style.top = '0';
          canvas.style.left = '0';
          canvas.style.width = '100%';
          canvas.style.height = '100%';
          canvas.style.pointerEvents = 'none';
          canvas.style.zIndex = '1';
          hero.style.position = 'relative';
          hero.appendChild(canvas);
          this.initWebGL(canvas);
        }
      } else {
        this.initWebGL(container);
      }
    } catch (error) {
      window.LandingV3Utils?.logError('Failed to initialize WebGL scene', error);
    }
  },

  initWebGL(canvas) {
    // Scene setup
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Camera position
    this.camera.position.z = 5;

    // Create logo geometry (simplified - can be enhanced with actual logo model)
    const geometry = new THREE.BoxGeometry(1, 1, 0.1);
    const material = new THREE.MeshBasicMaterial({ 
      color: 0xffd700,
      transparent: true,
      opacity: 0.8
    });
    this.logoMesh = new THREE.Mesh(geometry, material);
    this.scene.add(this.logoMesh);

    // Handle resize
    window.addEventListener('resize', window.LandingV3Utils?.debounce(() => {
      this.camera.aspect = canvas.clientWidth / canvas.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    }, 250));

    // Animation loop
    this.animate();

    window.LandingV3Utils?.logInfo('WebGL scene initialized');
  },

  animate() {
    if (!this.renderer || !this.scene || !this.camera) return;

    requestAnimationFrame(() => this.animate());

    // Rotate logo slowly
    if (this.logoMesh) {
      this.logoMesh.rotation.y += 0.005;
      this.logoMesh.rotation.x += 0.002;
    }

    this.renderer.render(this.scene, this.camera);
  }
};



