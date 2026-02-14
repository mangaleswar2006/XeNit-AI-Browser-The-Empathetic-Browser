from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# HYPERDRIVE SPLASH HTML
BOOT_SEQUENCE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        body { margin: 0; background: #000; overflow: hidden; font-family: 'Orbitron', sans-serif; }
        #canvas-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        
        #overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            background: radial-gradient(circle, transparent 0%, rgba(0,0,0,0.8) 100%);
        }
        
        /* CINEMATIC TITLE */
        .title-container {
            position: relative;
            z-index: 20;
            perspective: 500px;
        }
        
        .main-title {
            font-size: 8rem;
            font-weight: 900;
            color: transparent;
            -webkit-text-stroke: 4px #FFF;
            text-transform: uppercase;
            letter-spacing: 20px;
            opacity: 0;
            transform: scale(3) translateZ(100px);
            animation: impact-zoom 4s cubic-bezier(0.19, 1, 0.22, 1) forwards;
            text-shadow: 0 0 50px rgba(0, 240, 255, 0.8);
        }
        
        .main-title .fill {
            position: absolute;
            top: 0; left: 0;
            color: #FFF;
            overflow: hidden;
            width: 0%;
            animation: fill-text 2s 1.5s cubic-bezier(0.19, 1, 0.22, 1) forwards;
            -webkit-text-stroke: 0;
            white-space: nowrap;
        }

        @keyframes impact-zoom {
            0% { opacity: 0; transform: scale(5) translateZ(500px); filter: blur(20px); }
            10% { opacity: 1; transform: scale(1) translateZ(0); filter: blur(0px); }
            80% { transform: scale(1.05) translateZ(20px); }
            100% { transform: scale(20) translateZ(1000px); opacity: 0; } /* Warp out at end */
        }
        
        @keyframes fill-text {
            0% { width: 0%; }
            100% { width: 100%; }
        }

        .subtitle {
            margin-top: 20px;
            color: #00F0FF;
            font-size: 1.2rem;
            letter-spacing: 8px;
            opacity: 0;
            animation: fade-in 0.5s 1s forwards;
            text-shadow: 0 0 10px #00F0FF;
        }
        
        @keyframes fade-in {
            to { opacity: 1; }
        }

        /* STATUS BAR */
        .status-bar {
            position: absolute;
            bottom: 50px;
            width: 400px;
            height: 2px;
            background: rgba(255, 255, 255, 0.2);
        }
        
        .status-fill {
            width: 0%;
            height: 100%;
            background: #00F0FF;
            box-shadow: 0 0 20px #00F0FF;
            animation: load 3.5s linear forwards;
        }
        
        @keyframes load {
            0% { width: 0%; }
            100% { width: 100%; }
        }
        
        .status-text {
            position: absolute;
            bottom: 60px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.8rem;
            font-family: monospace;
            text-transform: uppercase;
        }

    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- Post Processing for Bloom (Optional/Heavy, doing manual Glow) -->
</head>
<body>
    <div id="canvas-container"></div>
    
    <div id="overlay">
        <div class="title-container">
            <div class="main-title">XENIT<span class="fill">XENIT</span></div>
        </div>
        <div class="subtitle" id="sub">HYPERDRIVE ONLINE</div>
        
        <div class="status-text" id="log">INITIALIZING WARP DRIVE...</div>
        <div class="status-bar"><div class="status-fill"></div></div>
    </div>

    <script>
        // --- HYPERDRIVE WARP ANIMATION ---
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x000000, 0.001); // Deep space black
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
        camera.position.z = 0;
        
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);
        
        // TUNNEL OF STARS
        const starCount = 6000;
        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(starCount * 3);
        const starVel = new Float32Array(starCount); // Individual speeds
        
        for(let i=0; i<starCount; i++) {
            // Spread in a long cylinder tunnel
            const x = (Math.random() - 0.5) * 2000;
            const y = (Math.random() - 0.5) * 2000;
            const z = (Math.random() - 0.5) * 2000; // Depth
            
            starPos[i*3] = x;
            starPos[i*3+1] = y;
            starPos[i*3+2] = z;
            
            starVel[i] = Math.random() * 2 + 0.5; // Random speed base
        }
        
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        
        // Use a streak texture or just stretched points? 
        // Points are simpler. We'll stretch them via velocity blur simulation visually (lines)
        const starMat = new THREE.PointsMaterial({
            color: 0xAAAAAA,
            size: 1.5,
            transparent: true,
            opacity: 0.8
        });
        
        const starSystem = new THREE.Points(starGeo, starMat);
        scene.add(starSystem);

        // CORE ANIMATION ARRAYS
        const positions = starSystem.geometry.attributes.position.array;

        let speed = 2;
        let shake = 0;
        
        function animate() {
            requestAnimationFrame(animate);
            
            // Accelerate
            if (speed < 80) speed *= 1.02;
            
            // Camera Shake Intensity increases with speed
            shake = (speed / 100) * 0.5;
            camera.position.x = (Math.random() - 0.5) * shake;
            camera.position.y = (Math.random() - 0.5) * shake;
            
            // Move Stars
            for(let i=0; i<starCount; i++) {
                // Move Towards Camera (Positive Z) or Away (Negative Z depending on setup)
                // Let's move them TOWARDS camera (Z increases)
                positions[i*3+2] += speed;
                
                // If passes camera (Z > 200), reset to far bg (Z = -1000)
                if (positions[i*3+2] > 200) {
                    positions[i*3+2] = -1500;
                    
                    // Reset X/Y to create randomized tunnel feel so we don't see patterns
                    // positions[i*3] = (Math.random() - 0.5) * 2000;
                    // positions[i*3+1] = (Math.random() - 0.5) * 2000;
                }
            }
            starSystem.geometry.attributes.position.needsUpdate = true;
            
            // Color Shift (Blue Shift at high speed)
            if (speed > 50) {
                starSystem.material.color.setHex(0xAAEEFF);
            }
            
            renderer.render(scene, camera);
        }
        
        animate();
        
        // Logs
        const logs = [
            "ENGAGING WARP DRIVE...",
            "NEURAL LINK ESTABLISHED...",
            "REALITY MATRIX LOADED...",
            "WELCOME PILOT."
        ];
        let lIndex = 0;
        const lDiv = document.getElementById('log');
        setInterval(() => {
            if (lIndex < logs.length) {
                lDiv.innerText = logs[lIndex];
                lIndex++;
            }
        }, 800);
        
        window.addEventListener('resize', () => {
             renderer.setSize(window.innerWidth, window.innerHeight);
             camera.aspect = window.innerWidth / window.innerHeight;
             camera.updateProjectionMatrix();
        });
    </script>
</body>
</html>
"""

class FuturisticSplash(QWidget):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Splash Config
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(800, 500) # Cinematic aspect
        
        # Center
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        self.move(x, y)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.web = QWebEngineView()
        self.web.setHtml(BOOT_SEQUENCE_HTML)
        self.web.setStyleSheet("background: black;")
        self.web.page().setBackgroundColor(Qt.GlobalColor.black)
        self.web.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        layout.addWidget(self.web)
        
        # Duration: 4.0s
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_splash)
        self.timer.start(4000) 
        
    def close_splash(self):
        self.finished.emit()
        self.close()
