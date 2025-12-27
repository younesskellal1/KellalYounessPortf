/*
  static/js/avatar.js

  Three.js-based AI assistant avatar loader.
  - Lazy-loads a GLB/GLTF model when the assistant container is visible
  - Applies the provided portrait as the face texture (see instructions below)
  - Mouse-based parallax (360-degree rotation feel)
  - Idle animations: subtle breathing, micro head movement, and optional blink
  - Lighting: soft key light + rim light
  - Performance: lazy load, limited pixel ratio, DRACO support if present

  Usage:
  1) Place your GLB model at: /static/models/assistant.glb (low-poly with proper UV map)
  2) Ensure the face material or mesh is named understandably (e.g. "Face" or material named "face")
  3) Place the portrait image at e.g. /static/images/assistant-face.jpg and update FACE_IMAGE_URL below
  4) The template includes a <canvas id="assistant-canvas"> where the scene will render

  Notes on blinking/morph targets:
  - If your GLB exports morph targets/blend shapes for blinking (common from Blender when using shape keys),
    ensure the morph is named "blink", "Blink" or contains "eye"; the loader will animate it if present.
  - If morph targets are not available, the script will still perform breathing and micro rotations.

*/
(function () {
  // Configuration - adjust paths if you move the model or face image
  const MODEL_URL = '/static/models/assistant.glb';
  // Public demo fallback (small, commonly available glTF) used only for preview if local model missing
  const DEMO_MODEL_URL = 'https://threejs.org/examples/models/gltf/LeePerrySmith/LeePerrySmith.glb';
  const FACE_IMAGE_URL = '/static/images/profile.png'; // default fallback

  // Idle animation settings
  const BREATH_AMPLITUDE = 0.015; // scale breathing
  const HEAD_NOD_AMPLITUDE = 0.03; // radians
  const BLINK_INTERVAL_MIN = 3000; // ms
  const BLINK_INTERVAL_MAX = 8000; // ms
  const CANVAS_ID = 'assistant-canvas';
  const CONTAINER_ID = 'assistant-container';
  const LOADER_ID = 'assistant-loader';

  // Wait until DOM ready
  function ready(fn) {
    if (document.readyState !== 'loading') return fn();
    document.addEventListener('DOMContentLoaded', fn);
  }

  ready(() => {
    const container = document.getElementById(CONTAINER_ID);
    const canvas = document.getElementById(CANVAS_ID);
    const loaderEl = document.getElementById(LOADER_ID);
    if (!container || !canvas) return;
    if (loaderEl) loaderEl.textContent = 'Preparing assistant…';

    // Lazy-load scene only when container is visible
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          io.disconnect();
          initScene(container, canvas, loaderEl);
        }
      });
    }, { threshold: 0.15 });

    io.observe(container);
  });

  function initScene(container, canvas, loaderEl) {
    // Load THREE if not available (assumes <script src="https://unpkg.com/three/..."> is in template)
    if (typeof THREE === 'undefined') {
      console.error('Three.js not found. Please include Three.js in your page.');
      if (loaderEl) loaderEl.textContent = 'Three.js missing';
      return;
    }

    const scene = new THREE.Scene();
    const clock = new THREE.Clock();

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(container.clientWidth, container.clientHeight, false);

    // Camera
    const camera = new THREE.PerspectiveCamera(35, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0.9, 2.8);

    // Lights: soft key + rim
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.0);
    keyLight.position.set(0.5, 1.0, 1.0);
    keyLight.castShadow = false;
    scene.add(keyLight);

    const fillLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0x88ccff, 0.6);
    rimLight.position.set(-0.6, 0.8, -1.2);
    scene.add(rimLight);

    // Root group for easy rotation
    const avatarGroup = new THREE.Group();
    scene.add(avatarGroup);

    // Ground (subtle) - optional plane for ambient occlusion feel
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(10, 10),
      new THREE.MeshStandardMaterial({ color: 0x000000, metalness: 0, roughness: 1, opacity: 0, transparent: true })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -1.2;
    avatarGroup.add(ground);

  // Loaders
  const gltfLoader = new THREE.GLTFLoader();

    // Optionally enable DRACO if DRACOLoader is present on THREE
    if (THREE.DRACOLoader) {
      const dracoLoader = new THREE.DRACOLoader();
      // Default path for Draco decoder; adjust if you host locally
      dracoLoader.setDecoderPath('https://unpkg.com/three@0.158.0/examples/js/libs/draco/');
      gltfLoader.setDRACOLoader(dracoLoader);
    }

    let model = null;
    let faceMesh = null; // mesh that will receive the portrait texture
    let blinkMixer = null;
    let blinkTrack = null;

    // Helper: apply face texture to mesh/materials that look like face
    function applyFaceTexture(texture) {
      texture.encoding = THREE.sRGBEncoding;
      texture.flipY = false; // glTF uses UVs that expect flipY = false

      if (!model) return;

      // Strategy: find candidate materials or meshes by name
      model.scene.traverse((node) => {
        if (node.isMesh) {
          const name = (node.name || '').toLowerCase();
          const matName = (node.material && node.material.name) ? node.material.name.toLowerCase() : '';

          // Heuristics: 'face', 'skin', 'head' in name or material name
          if (name.includes('face') || name.includes('skin') || name.includes('head') || matName.includes('face') || matName.includes('skin')) {
            // Replace color/map while preserving other material properties
            if (Array.isArray(node.material)) {
              node.material.forEach((m) => {
                m.map = texture;
                m.needsUpdate = true;
              });
            } else {
              node.material.map = texture;
              node.material.needsUpdate = true;
            }
            faceMesh = node;
          }
        }
      });

      // If we didn't find a clear candidate, try to apply to the first skinned mesh
      if (!faceMesh) {
        model.scene.traverse((node) => {
          if (!faceMesh && node.isSkinnedMesh) {
            node.material.map = texture;
            node.material.needsUpdate = true;
            faceMesh = node;
          }
        });
      }
    }

    // Before loading, check whether local model exists (so we can give useful feedback).
    async function resolveModelUrl(url) {
      try {
        const res = await fetch(url, { method: 'HEAD' });
        if (res.ok) return url;
        return DEMO_MODEL_URL;
      } catch (e) {
        // Network error or blocked (fall back to demo model)
        return DEMO_MODEL_URL;
      }
    }

    (async () => {
      const resolvedUrl = await resolveModelUrl(MODEL_URL);
      if (loaderEl) loaderEl.textContent = resolvedUrl === MODEL_URL ? 'Loading assistant…' : 'Loading demo assistant…';

      // safety timeout to show an error if loading stalls
      let loadTimedOut = false;
      const loadTimeout = setTimeout(() => {
        loadTimedOut = true;
        if (loaderEl) loaderEl.textContent = 'Taking longer than usual to load the assistant...';
      }, 10000);

      // Load model lazily
      gltfLoader.load(
        resolvedUrl,
      (gltf) => {
        model = gltf;

        // Normalize scale and center
        const box = new THREE.Box3().setFromObject(gltf.scene);
        const size = new THREE.Vector3();
        box.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 1.6 / maxDim; // target size
        gltf.scene.scale.setScalar(scale);

        // Center
        box.setFromObject(gltf.scene);
        box.getCenter(size);
        gltf.scene.position.sub(size);

        avatarGroup.add(gltf.scene);

        // Try to find animation/morph targets for blinking
        if (gltf.animations && gltf.animations.length) {
          blinkMixer = new THREE.AnimationMixer(gltf.scene);
          // Look for any animation that seems like blink
          const blinkClip = gltf.animations.find(a => /blink/i.test(a.name));
          if (blinkClip) {
            const action = blinkMixer.clipAction(blinkClip);
            action.setLoop(THREE.LoopOnce, 1);
            action.clampWhenFinished = true;
            // We'll trigger this action on intervals for blinking
            blinkTrack = action;
          }
        }

        // If morph targets exist on meshes, find a blink key
        // We'll search morphTargetDictionary for keys like 'blink' and animate them manually
        let morphTargets = [];
        gltf.scene.traverse((node) => {
          if (node.isMesh && node.morphTargetInfluences && node.morphTargetDictionary) {
            const dict = node.morphTargetDictionary;
            Object.keys(dict).forEach((k) => {
              if (/blink/i.test(k)) morphTargets.push({ node, index: dict[k] });
            });
          }
        });

        // Load face texture and apply
        const texLoader = new THREE.TextureLoader();
        texLoader.load(FACE_IMAGE_URL, (tex) => {
          applyFaceTexture(tex);
          if (loaderEl) loaderEl.style.display = 'none';
        }, undefined, (err) => {
          console.warn('Face texture failed to load:', err);
          if (loaderEl) loaderEl.textContent = 'Assistant (no texture)';
        });

        // If there are morph target blink candidates, schedule blinking
        if (morphTargets.length) {
          scheduleBlink(() => {
            // animate influences quickly
            morphTargets.forEach(({ node, index }) => {
              // quick blink timeline
              const now = performance.now();
              animateMorph(node, index, 0.0, 1.0, 80, () => {
                animateMorph(node, index, 1.0, 0.0, 120);
              });
            });
          });
        } else if (blinkTrack) {
          // Use animation clip if available
          scheduleBlink(() => {
            blinkTrack.reset();
            blinkTrack.play();
            setTimeout(() => blinkTrack.stop(), 600);
          });
        }
      },
        (progress) => {
          if (loaderEl) {
            if (progress.total) {
              const pct = Math.round((progress.loaded / progress.total) * 100);
              loaderEl.textContent = 'Loading assistant ' + pct + '%';
            } else {
              // Unknown total size - show loaded KB
              const kb = Math.round((progress.loaded || 0) / 1024);
              loaderEl.textContent = 'Loading assistant ' + kb + ' KB';
            }
          }
        },
        (err) => {
          clearTimeout(loadTimeout);
          console.error('Failed to load model', err);
          if (loaderEl) loaderEl.textContent = 'Failed to load assistant (see console)';
        },
        () => {
          // on complete (three.js uses onProgress/onError differently across versions; keep fallback)
          clearTimeout(loadTimeout);
          if (loaderEl && !loadTimedOut) loaderEl.style.display = 'none';
        }
      );
    })();

    // Mouse interaction - map pointer to rotation
    let pointerX = 0, pointerY = 0; // normalized -1..1
    function onPointerMove(e) {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      pointerX = (x - 0.5) * 2; // -1..1
      pointerY = (y - 0.5) * 2; // -1..1
    }
    container.addEventListener('pointermove', onPointerMove);
    container.addEventListener('pointerleave', () => { pointerX = 0; pointerY = 0; });

    // Resize handling
    function resize() {
      const w = container.clientWidth;
      const h = container.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }

    window.addEventListener('resize', resize);
    resize();

    // Simple helper to interpolate morph values
    function animateMorph(node, index, from, to, duration, onComplete) {
      const start = performance.now();
      function frame() {
        const t = Math.min(1, (performance.now() - start) / duration);
        const val = from + (to - from) * t;
        if (node.morphTargetInfluences) node.morphTargetInfluences[index] = val;
        if (t < 1) requestAnimationFrame(frame);
        else if (onComplete) onComplete();
      }
      frame();
    }

    function scheduleBlink(cb) {
      const next = BLINK_INTERVAL_MIN + Math.random() * (BLINK_INTERVAL_MAX - BLINK_INTERVAL_MIN);
      setTimeout(() => {
        try { cb(); } catch (e) { console.warn('Blink failed:', e); }
        scheduleBlink(cb);
      }, next);
    }

    // Idle animation bookkeeping
    let lastTime = 0;
    function animate() {
      const t = clock.getElapsedTime();

      // subtle breathing (scale)
      const breath = 1 + Math.sin(t * 1.1) * BREATH_AMPLITUDE;
      avatarGroup.scale.set(breath, breath, breath);

      // micro head movement: nod + mouse parallax
      const targetY = pointerX * 0.6; // rotation around Y (look left/right)
      const targetX = pointerY * 0.25; // rotation around X (pitch)

      // head nod oscillation
      const nod = Math.sin(t * 0.5) * HEAD_NOD_AMPLITUDE;

      // Apply to avatarGroup for whole-head movement
      avatarGroup.rotation.y += (targetY - avatarGroup.rotation.y) * 0.08;
      avatarGroup.rotation.x += ((targetX + nod) - avatarGroup.rotation.x) * 0.08;

      // Update any animation mixer
      if (typeof blinkMixer !== 'undefined' && blinkMixer) blinkMixer.update(clock.getDelta());

      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    animate();

    // Public helper: allow programmatic replacement of face texture
    window.replaceAssistantFace = function (imageUrl) {
      const tex = new THREE.TextureLoader().load(imageUrl, (texture) => {
        applyFaceTexture(texture);
      });
    };

    // Accessibility: if user provides a data-face attribute on container, use it
    const dataFace = container.getAttribute('data-face');
    if (dataFace) {
      window.replaceAssistantFace(dataFace);
    }
  }

})();
