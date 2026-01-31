/**
 * 3D Visualizer Utilities
 * Helper functions for Three.js visualizations
 */

// ===================================
// Common 3D Utilities
// ===================================

class Visualizer3D {
    constructor(canvasId, containerId) {
        this.canvas = document.getElementById(canvasId);
        this.container = document.getElementById(containerId);

        if (!this.canvas || !this.container) {
            console.warn(`3D Visualizer: Canvas or container not found`);
            return;
        }

        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.offsetWidth / this.container.offsetHeight,
            0.1,
            1000
        );
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            alpha: true,
            antialias: true
        });

        this.renderer.setSize(this.container.offsetWidth, this.container.offsetHeight);
        this.camera.position.z = 5;

        // Handle resize
        window.addEventListener('resize', () => this.onResize());
    }

    onResize() {
        if (!this.container || !this.camera || !this.renderer) return;

        this.camera.aspect = this.container.offsetWidth / this.container.offsetHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.offsetWidth, this.container.offsetHeight);
    }

    animate(callback) {
        const loop = () => {
            requestAnimationFrame(loop);
            if (callback) callback();
            this.renderer.render(this.scene, this.camera);
        };
        loop();
    }

    addObject(object) {
        this.scene.add(object);
    }

    clear() {
        while (this.scene.children.length > 0) {
            this.scene.remove(this.scene.children[0]);
        }
    }
}

// ===================================
// Particle System
// ===================================

class ParticleSystem {
    constructor(count = 100) {
        this.count = count;
        this.particles = [];
        this.geometry = new THREE.BufferGeometry();
        this.material = new THREE.PointsMaterial({
            color: 0x667eea,
            size: 0.05,
            transparent: true,
            opacity: 0.6
        });

        this.createParticles();
        this.points = new THREE.Points(this.geometry, this.material);
    }

    createParticles() {
        const positions = [];
        const velocities = [];

        for (let i = 0; i < this.count; i++) {
            positions.push(
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 10
            );

            velocities.push(
                (Math.random() - 0.5) * 0.02,
                (Math.random() - 0.5) * 0.02,
                (Math.random() - 0.5) * 0.02
            );
        }

        this.geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        this.velocities = velocities;
    }

    update() {
        const positions = this.geometry.attributes.position.array;

        for (let i = 0; i < this.count; i++) {
            const i3 = i * 3;

            positions[i3] += this.velocities[i3];
            positions[i3 + 1] += this.velocities[i3 + 1];
            positions[i3 + 2] += this.velocities[i3 + 2];

            // Wrap around
            ['x', 'y', 'z'].forEach((axis, idx) => {
                if (Math.abs(positions[i3 + idx]) > 5) {
                    positions[i3 + idx] *= -1;
                }
            });
        }

        this.geometry.attributes.position.needsUpdate = true;
    }

    getPoints() {
        return this.points;
    }
}

// ===================================
// Audio Reactive Sphere
// ===================================

class AudioReactiveSphere {
    constructor(radius = 2, color = 0x667eea) {
        const geometry = new THREE.IcosahedronGeometry(radius, 4);
        const material = new THREE.MeshPhongMaterial({
            color: color,
            flatShading: true,
            transparent: true,
            opacity: 0.8
        });

        this.mesh = new THREE.Mesh(geometry, material);
        this.baseRadius = radius;
        this.audioData = null;
    }

    setAudioData(data) {
        this.audioData = data;
    }

    update() {
        // Rotate
        this.mesh.rotation.x += 0.005;
        this.mesh.rotation.y += 0.01;

        // React to audio
        if (this.audioData && this.audioData.length > 0) {
            const avg = this.audioData.reduce((a, b) => a + b, 0) / this.audioData.length;
            const scale = 1 + (avg / 255) * 0.5;
            this.mesh.scale.set(scale, scale, scale);
        }
    }

    getMesh() {
        return this.mesh;
    }
}

// ===================================
// Waveform Bars
// ===================================

class WaveformBars {
    constructor(count = 64) {
        this.count = count;
        this.bars = [];

        this.createBars();
    }

    createBars() {
        const barWidth = 0.8;
        const spacing = 1.2;

        for (let i = 0; i < this.count; i++) {
            const geometry = new THREE.BoxGeometry(barWidth, 1, barWidth);
            const hue = 0.6 + (i / this.count) * 0.2;
            const material = new THREE.MeshBasicMaterial({
                color: new THREE.Color().setHSL(hue, 0.8, 0.5)
            });
            const bar = new THREE.Mesh(geometry, material);

            bar.position.x = (i - this.count / 2) * spacing;
            bar.position.y = 0;

            this.bars.push(bar);
        }
    }

    setAudioData(data) {
        if (!data) return;

        this.bars.forEach((bar, i) => {
            const value = data[i] || 0;
            const scale = (value / 255) * 20 + 1;
            bar.scale.y = scale;
            bar.position.y = scale / 2;
        });
    }

    idleAnimation() {
        const time = Date.now() * 0.001;

        this.bars.forEach((bar, i) => {
            const scale = Math.sin(time + i * 0.1) * 2 + 3;
            bar.scale.y = scale;
            bar.position.y = scale / 2;
        });
    }

    getBars() {
        return this.bars;
    }
}

// ===================================
// Utility Functions
// ===================================

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function lerp(start, end, t) {
    return start + (end - start) * t;
}

function easeInOutCubic(t) {
    return t < 0.5
        ? 4 * t * t * t
        : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// Export for use in other files
window.Visualizer3D = Visualizer3D;
window.ParticleSystem = ParticleSystem;
window.AudioReactiveSphere = AudioReactiveSphere;
window.WaveformBars = WaveformBars;
