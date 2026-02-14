def get_new_tab_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>XeNit</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

            body { 
                margin: 0; 
                overflow: hidden; 
                background-color: #000; 
                font-family: 'Inter', sans-serif; 
            }
            
            /* Fix white flash */
            html { background-color: #000; }
            
            canvas { 
                display: block; 
                position: fixed; 
                top: 0; left: 0; 
                z-index: 1; 
            }
            
            #ui-layer {
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                z-index: 10;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                pointer-events: none;
                transform-style: preserve-3d;
                perspective: 1000px;
            }

            .interactive { pointer-events: auto; }

            /* SEARCH BAR AREA */
            .search-container {
                width: 100%;
                max-width: 650px;
                position: relative;
                margin-top: 15vh;
                z-index: 100; /* Ensure search is always on top */
            }

            .search-input {
                width: 100%;
                padding: 20px 20px 20px 60px;
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(10, 10, 10, 0.7);
                color: #FFF;
                font-size: 1.2rem;
                backdrop-filter: blur(15px);
                transition: all 0.3s;
                outline: none;
                box-sizing: border-box;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }

            .search-input:focus {
                border-color: #00F0FF;
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
                background: rgba(0, 0, 0, 0.9);
                border-bottom-left-radius: 0; /* Flatten bottom for dropdown */
                border-bottom-right-radius: 0;
            }
            
            .search-icon {
                position: absolute;
                left: 20px;
                top: 24px;
                width: 24px;
                height: 24px;
                fill: #888;
                pointer-events: none;
            }

            /* SUGGESTIONS DROPDOWN */
            .suggestions-dropdown {
                position: absolute;
                top: 100%;
                left: 0;
                width: 100%;
                background: rgba(10, 10, 10, 0.9);
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-top: none;
                border-radius: 0 0 30px 30px;
                backdrop-filter: blur(15px);
                display: none;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            
            .suggestion-item {
                padding: 12px 20px 12px 60px;
                color: #DDD;
                font-size: 1rem;
                cursor: pointer;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                transition: background 0.2s;
                display: flex;
                align-items: center;
            }
            
            .suggestion-item:last-child {
                border-bottom: none;
            }
            
            .suggestion-item:hover {
                background: rgba(0, 240, 255, 0.1);
                color: #FFF;
            }
            
            .suggestion-icon {
                margin-right: 15px;
                width: 16px;
                height: 16px;
                fill: #666;
            }

            /* SHORTCUTS */
            .shortcuts {
                margin-top: 50px;
                display: flex;
                gap: 30px;
                z-index: 20;
            }

            .shortcut {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                text-align: center;
                transform: translateZ(0); /* Stability */
            }

            .shortcut:hover {
                transform: translateY(-5px);
            }

            .icon-box {
                width: 60px;
                height: 60px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease-out;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                margin-bottom: 10px;
            }

            .shortcut:hover .icon-box {
                background: rgba(0, 240, 255, 0.25);
                border-color: #00F0FF;
                box-shadow: 0 0 30px rgba(0, 240, 255, 0.8), inset 0 0 10px rgba(0, 240, 255, 0.5);
                transform: scale(1.05);
            }

            .shortcut span {
                color: #AAA;
                font-size: 0.85rem;
                font-weight: 500;
                transition: color 0.3s;
                letter-spacing: 0.5px;
            }

            .shortcut:hover span {
                color: #FFF;
            }

            .app-icon {
                width: 32px;
                height: 32px;
                fill: #EAEAEA;
                transition: fill 0.3s;
            }
            
            .shortcut:hover .app-icon {
                fill: #00F0FF;
            }
            
            /* LOGO - 3D RESTORED BUT SAFE */
            .main-logo {
                font-family: 'Orbitron', sans-serif;
                font-size: 8rem;
                color: transparent;
                -webkit-text-stroke: 2px rgba(0, 240, 255, 0.8);
                position: absolute;
                top: 30%;
                left: 50%;
                /* Default center */
                transform: translate(-50%, -50%); 
                z-index: 50; /* Higher than shortcuts */
                font-weight: 900;
                text-align: center;
                letter-spacing: -5px;
                pointer-events: auto;
                cursor: default;
                /* Shadows/Glow */
                filter: drop-shadow(0 0 20px rgba(0, 240, 255, 0.3));
                /* Important for 3D rotation not to cut off */
                transform-style: preserve-3d;
                backface-visibility: hidden;
            }
            
            .main-logo:hover {
                -webkit-text-stroke: 2px #00F0FF;
                filter: drop-shadow(0 0 40px rgba(0, 240, 255, 0.6));
            }

        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <div id="ui-layer">
            <div class="main-logo interactive" id="logoText">XeNit</div>
            
            <div class="search-container interactive">
                <svg class="search-icon" viewBox="0 0 24 24">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
                <input type="text" class="search-input" placeholder="Search the future..." id="searchInput" autocomplete="off">
                <div class="suggestions-dropdown" id="suggestions">
                    <!-- Items injected here -->
                </div>
            </div>

            <div class="shortcuts interactive">
                <a class="shortcut" href="https://youtube.com">
                    <div class="icon-box">
                        <svg class="app-icon" viewBox="0 0 24 24">
                            <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
                        </svg>
                    </div>
                    <span>YouTube</span>
                </a>
                <a class="shortcut" href="https://google.com">
                    <div class="icon-box">
                        <svg class="app-icon" viewBox="0 0 24 24">
                            <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                        </svg>
                    </div>
                    <span>Google</span>
                </a>
                <a class="shortcut" href="https://reddit.com">
                    <div class="icon-box">
                        <svg class="app-icon" viewBox="0 0 24 24">
                            <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
                        </svg>
                    </div>
                    <span>Reddit</span>
                </a>
                <a class="shortcut" href="https://github.com">
                    <div class="icon-box">
                        <svg class="app-icon" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                    </div>
                    <span>GitHub</span>
                </a>
            </div>
        </div>

        <script>
            // --- THREE.JS SCENE SETUP ---
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x000000, 0.001);

            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 50;

            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.body.appendChild(renderer.domElement);

            // --- PARTICLES ---
            const particleCount = 2000;
            const posArray = new Float32Array(particleCount * 3);
            for(let i = 0; i < particleCount * 3; i++) {
                posArray[i] = (Math.random() - 0.5) * 300; 
            }
            const particlesGeo = new THREE.BufferGeometry();
            particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            const particlesMat = new THREE.PointsMaterial({
                size: 0.5, color: 0x00F0FF, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending
            });
            const particlesMesh = new THREE.Points(particlesGeo, particlesMat);
            scene.add(particlesMesh);

            // --- GEOMETRIC SHAPES ---
            const shapesGroup = new THREE.Group();
            scene.add(shapesGroup);
            const geoHighlight = new THREE.IcosahedronGeometry(1, 0);
            const matHighlight = new THREE.MeshBasicMaterial({ color: 0x00F0FF, wireframe: true });
            for(let i=0; i<20; i++) {
                const mesh = new THREE.Mesh(geoHighlight, matHighlight);
                mesh.position.set(
                    (Math.random() - 0.5) * 100,
                    (Math.random() - 0.5) * 60,
                    (Math.random() - 0.5) * 50
                );
                mesh.rotation.set(Math.random(), Math.random(), 0);
                shapesGroup.add(mesh);
            }

            // --- SMOOTH TRACKING (LERP) ---
            let targetX = 0, targetY = 0;
            let mouseX = 0, mouseY = 0;
            const windowHalfX = window.innerWidth / 2;
            const windowHalfY = window.innerHeight / 2;
            
            document.addEventListener('mousemove', (event) => {
                targetX = (event.clientX - windowHalfX) * 0.001; 
                targetY = (event.clientY - windowHalfY) * 0.001;
            });

            // --- SEARCH SUGGESTIONS LOGIC ---
            const searchInput = document.getElementById('searchInput');
            const suggestionsBox = document.getElementById('suggestions');
            
            searchInput.addEventListener('input', async (e) => {
                const query = e.target.value;
                if(query.length === 0) {
                    suggestionsBox.style.display = 'none';
                    return;
                }
                
                // Fetch suggestions from Google
                try {
                    const response = await fetch(`https://www.google.com/complete/search?client=firefox&q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    const suggestions = data[1]; // Array of strings
                    
                    if(suggestions.length > 0) {
                        suggestionsBox.innerHTML = '';
                        suggestions.slice(0, 5).forEach(text => {
                            const div = document.createElement('div');
                            div.className = 'suggestion-item';
                            // Use a generic search icon for items
                            div.innerHTML = `<svg class="suggestion-icon" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg> ${text}`;
                            div.onclick = () => {
                                window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(text);
                            };
                            suggestionsBox.appendChild(div);
                        });
                        suggestionsBox.style.display = 'flex';
                        
                        // Round corners differently when open
                        searchInput.style.borderBottomLeftRadius = '0';
                        searchInput.style.borderBottomRightRadius = '0';
                    } else {
                        suggestionsBox.style.display = 'none';
                        searchInput.style.borderBottomLeftRadius = '30px';
                        searchInput.style.borderBottomRightRadius = '30px';
                    }
                } catch (err) {
                    // console.error(err);
                }
            });
            
            // Hide on click outside
            document.addEventListener('click', (e) => {
                if(!e.target.closest('.search-container')) {
                    suggestionsBox.style.display = 'none';
                    searchInput.style.borderBottomLeftRadius = '30px';
                    searchInput.style.borderBottomRightRadius = '30px';
                }
            });

            // --- ANIMATION LOOP ---
            const clock = new THREE.Clock();

            function animate() {
                requestAnimationFrame(animate);
                const time = clock.getElapsedTime();
                
                // LERP
                mouseX += (targetX - mouseX) * 0.05;
                mouseY += (targetY - mouseY) * 0.05;

                // Rotations
                particlesMesh.rotation.y = time * 0.02 + mouseX * 2;
                particlesMesh.rotation.x = mouseY * 2;

                shapesGroup.children.forEach((mesh, i) => {
                    mesh.rotation.x += 0.002;
                    mesh.rotation.y += 0.005;
                    mesh.position.y += Math.sin(time * 0.5 + i) * 0.05;
                });
                
                // Camera Sway
                camera.position.x += (mouseX * 5 - camera.position.x) * 0.1;
                camera.position.y += (-mouseY * 5 - camera.position.y) * 0.1;
                camera.lookAt(scene.position);

                // --- 3D LOGO RESTORED (SMOOTH LERP) ---
                const logo = document.getElementById('logoText');
                if(logo) {
                    const tiltX = -mouseY * 25; // Tilt up/down
                    const tiltY = mouseX * 25;  // Tilt left/right
                    
                    // We need to keep translate(-50%, -50%) to stay centered
                    logo.style.transform = `translate(-50%, -50%) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
                }

                renderer.render(scene, camera);
            }
            animate();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            document.getElementById('searchInput').addEventListener('keypress', function (e) {
                if (e.key === 'Enter' && this.value) {
                    window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(this.value);
                }
            });
        </script>
    </body>
    </html>
    """
