from PyQt6.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel, QMenu, QSizePolicy, QPushButton,
                             QSplitter, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer
from PyQt6.QtGui import QIcon, QAction, QColor
import os
import urllib.parse

from browser.tabs import TabManager
from browser.menu import CustomMenu
from browser.data_manager import DataManager
from browser.sidebar import Sidebar
from browser.dialogs import (HistoryDialog, BookmarksDialog, DownloadsDialog, 
                             SettingsDialog, HelpDialog, SignInDialog)
from browser.memory import MemoryManager
from browser.ai_agent import AIAgent
from browser.voice import VoiceManager
from browser.overlays import EmotionNotification
from browser.medical_safety import (check_health_search, get_safety_banner_js,
                                    check_untrusted_medical_site, get_untrusted_site_banner_js)

from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # PERSISTENCE: Configure Profile for Saving Login Data (WhatsApp, Gmail, etc.)
        self.base_dir = os.path.join(os.path.expanduser("~"), ".xenit_browser")
        self.profile_dir = os.path.join(self.base_dir, "profile")
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)

        profile = QWebEngineProfile("XeNitProfile", self)
        profile.setPersistentStoragePath(self.profile_dir)
        profile.setCachePath(self.profile_dir)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        # Use a specific, common Chrome version to pass security checks
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36")
        
        print(f"XeNit Profile Path set to: {self.profile_dir}")
        self.global_profile = profile

        # PERFORMANCE: Enable Smooth Scrolling & GPU Acceleration
        settings = profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        
        self.setWindowTitle("XeNit Browser")
        self.resize(1200, 800)
        
        self.data_manager = DataManager()
        self.voice_manager = VoiceManager()
        
        # Initialize AI Agent System
        self.memory_manager = MemoryManager()
        self.agent = AIAgent(self.memory_manager)
        
        # Initialize Overlays
        self.emotion_popup = EmotionNotification(self)
        
        # Emotion History for Fight Detection
        self.emotion_history = [] # Stores (timestamp, emotion)
        
        # Burnout Prevention Tracking
        import time
        self.work_start_time = time.time()
        self.last_break_time = time.time()
        self.stress_score = 0
        self.burnout_keywords = ["classroom", "docs", "canvas", "study", "exam", "deadline", "project", "homework", "math", "physics"]
        self.burnout_keywords = ["classroom", "docs", "canvas", "study", "exam", "deadline", "project", "homework", "math", "physics"]
        self.stress_search_terms = ["stress", "tired", "can't focus", "burnout", "anxiety", "fail", "quit"]
        
        self.emotional_keywords = {
            "loneliness": ["lonely", "alone", "no one cares", "isolated", "no friends"],
            "anxiety": ["stressed", "anxious", "panic", "overwhelmed", "nervous"],
            "depression": ["sad", "depressed", "hopeless", "pointless", "kill myself", "suicide", "end it"],
            "distress": ["need help", "struggling", "can't take it", "give up"]
        }
        
        # Burnout Timer (Checks every minute)
        self.burnout_timer = QTimer()
        self.burnout_timer.timeout.connect(self.monitor_burnout)
        self.burnout_timer.start(60000) # 1 minute interval
        
        # setup Controller for Agent Actions
        class AgentController:
            def __init__(self, window):
                self.window = window
            
            def open_url(self, url):
                # Ensure URL has scheme
                if "://" not in url:
                    url = "https://" + url
                return self.window.add_new_tab(QUrl(url), "Loading...")
                
            def play_music(self, query):
                # Search on YouTube
                search_url = f"https://www.youtube.com/results?search_query={query}"
                browser = self.open_url(search_url)
                
                def auto_play():
                    # Robust JS: Polls for the video title link for up to 10 seconds
                    js_code = """
                    (function() {
                        let attempts = 0;
                        const maxAttempts = 40; // 20 seconds (40 * 500ms)
                        
                        const interval = setInterval(function() {
                            attempts++;
                            // Selector for the first video title in search results
                            // Try multiple valid selectors
                            let video = document.querySelector('ytd-video-renderer #video-title') || 
                                        document.querySelector('a#video-title') ||
                                        document.querySelector('ytd-video-renderer a#thumbnail');
                            
                            if (video) {
                                console.log("XeNit AI: Found video, clicking...");
                                video.click();
                                // Fallback: If click is intercepted, force navigation
                                // Use a small timeout to let the click try first
                                setTimeout(() => {
                                    if(document.location.href.includes('results')) {
                                        window.location.href = video.href;
                                    }
                                }, 500);
                                clearInterval(interval);
                            } else if (attempts >= maxAttempts) {
                                console.log("XeNit AI: Could not find video to auto-play.");
                                clearInterval(interval);
                            }
                        }, 500); 
                    })();
                    """
                    browser.page().runJavaScript(js_code)
                    # Disconnect to avoid re-running if user navigates elsewhere in this tab
                    try:
                        browser.loadFinished.disconnect(auto_play)
                    except:
                        pass
                
                browser.loadFinished.connect(auto_play)
                
            def open_whatsapp(self, param=None):
                url = "https://web.whatsapp.com"
                phone = None
                message = param
                
                # Check if param contains number and message separated by |
                if param and "|" in param:
                    parts = param.split("|", 1)
                    phone = parts[0].strip()
                    message = parts[1].strip()
                
                if message:
                    encoded_msg = urllib.parse.quote(message)
                    if phone:
                         # Direct Message Link
                         url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
                    else:
                         # Select Contact Link
                         url = f"https://web.whatsapp.com/send?text={encoded_msg}"
                         
                browser = self.open_url(url)
                
                # Auto-Click Send Button
                def auto_send():
                    js_code = """
                    (function() {
                        let attempts = 0;
                        const maxAttempts = 60; // 30 seconds
                        
                        const interval = setInterval(function() {
                            attempts++;
                            
                            // 1. Try finding the Send Button
                            const sendBtnInfo = document.querySelector('span[data-icon="send"]');
                            const sendBtnAria = document.querySelector('button[aria-label="Send"]');
                            const mainBtn = (sendBtnInfo ? sendBtnInfo.closest('button') : null) || sendBtnAria;
                            
                            if (mainBtn) {
                                console.log("XeNit AI: Found Send button, clicking...");
                                mainBtn.click();
                                clearInterval(interval);
                                return;
                            }
                            
                            // 2. Fallback: Press 'Enter' if text box is focused (WhatsApp usually focuses it)
                            // We wait a bit (e.g. 10 attempts / 5s) before trying this to let the UI load
                            if (attempts > 10 && attempts % 5 === 0) {
                                const active = document.activeElement;
                                if (active && active.innerText.length > 0) {
                                    console.log("XeNit AI: Simulating Enter Key...");
                                    const event = new KeyboardEvent('keydown', {
                                        key: 'Enter',
                                        code: 'Enter',
                                        which: 13,
                                        keyCode: 13,
                                        bubbles: true
                                    });
                                    active.dispatchEvent(event);
                                    // We don't clear interval yet, in case it didn't work
                                }
                            }

                            if (attempts >= maxAttempts) {
                                console.log("XeNit AI: Could not find Send button.");
                                clearInterval(interval);
                            }
                        }, 500);
                    })();
                    """
                    browser.page().runJavaScript(js_code)
                    try:
                        browser.loadFinished.disconnect(auto_send)
                    except:
                        pass
                
                if message and phone:
                     # Only auto-send if we have a target
                     browser.loadFinished.connect(auto_send)
                
            def auto_fill(self, json_str):
                # We expect a JSON string like {"Name": "Lucky"}
                # To be safe against sloppy LLM output, we pass it directly to JS to parse if possible,
                # or we try to clean it here.
                # Let's wrap it in a JS function that handles the parsing.
                
                js_code = f"""
                (function() {{
                    try {{
                        const data = {json_str}; 
                        console.log("XeNit AutoFill Data:", data);
                        
                        for (const [key, value] of Object.entries(data)) {{
                            // Break key into searchable terms (e.g. "First Name" -> ["first", "name"])
                            const searchTerms = key.toLowerCase().split(/\s+|_|-/).filter(t => t.length > 0);
                            
                            let inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea, select'));
                            let bestMatch = null;
                            let maxScore = 0;
                            
                            for (let input of inputs) {{
                                let score = 0;
                                // Combine all potential identifiers
                                const content = (input.placeholder || input.name || input.id || "").toLowerCase();
                                const labelText = input.labels?.[0]?.innerText.toLowerCase() || "";
                                const ariaLabel = (input.getAttribute('aria-label') || "").toLowerCase();
                                const totalText = content + " " + labelText + " " + ariaLabel;
                                
                                // Scoring: Match count of terms
                                for(let term of searchTerms) {{
                                    if(totalText.includes(term)) score++;
                                }}
                                
                                // Bonus for exact match or starting with main term
                                if(totalText.includes(key.toLowerCase())) score += 2;
                                if(searchTerms.length > 0 && totalText.includes(searchTerms[0])) score += 0.5;

                                // Penalties for mismatch types? (e.g. email filling a phone field)
                                // Basic type checking
                                if (key.toLowerCase().includes("email") && input.type === "email") score += 2;
                                if (key.toLowerCase().includes("phone") && (input.type === "tel" || input.name.includes("phone"))) score += 2;
                                
                                if (score > maxScore) {{
                                    maxScore = score;
                                    bestMatch = input;
                                }}
                            }}
                            
                            if (bestMatch && maxScore > 0) {{
                                bestMatch.scrollIntoView({{behavior: "smooth", block: "center"}});
                                bestMatch.focus();
                                bestMatch.value = value;
                                bestMatch.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                bestMatch.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                bestMatch.blur();
                                console.log("XeNit Filled: " + key + " -> " + (bestMatch.name || bestMatch.id));
                            }} else {{
                                console.log("XeNit: Could not match field for " + key);
                            }}
                        }}
                    }} catch (e) {{
                        console.error("AutoFill Error:", e);
                    }}
                }})();
                """
                self.window.tabs.currentWidget().page().runJavaScript(js_code)

            def click_element(self, text):
                # Clicks a button or link containing the text
                js_code = f"""
                (function() {{
                    const text = "{text}".toLowerCase();
                    const elements = document.querySelectorAll('button, a, input[type="submit"], span');
                    
                    for (let el of elements) {{
                        if (el.innerText.toLowerCase().includes(text) || (el.value && el.value.toLowerCase().includes(text))) {{
                            console.log("XeNit Clicking:", el);
                            el.click();
                            return;
                        }}
                    }}
                    console.log("XeNit: No element found for " + text);
                }})();
                """
                self.window.tabs.currentWidget().page().runJavaScript(js_code)
                
            def close_specific_tabs(self, indices_str):
                # indices_str might be "[1, 3, 5]" string or list
                try:
                    import json
                    if isinstance(indices_str, str):
                        indices = json.loads(indices_str)
                    else:
                        indices = indices_str
                    
                    # Sort descending to avoid index shift issues
                    indices.sort(reverse=True)
                    for i in indices:
                         # Safety check: Don't close current tab if possible?
                         # Actually Agent can close content in background.
                         if i < self.window.tabs.count():
                             # Retrieve widget to explicitly delete it (release memory)
                             widget = self.window.tabs.widget(i)
                             self.window.tabs.removeTab(i)
                             if widget:
                                 widget.deleteLater()
                                 
                    print(f"XeNit Agent: Closed {len(indices)} tabs.")
                except Exception as e:
                    print(f"XeNit: Error closing tabs {e}")
                
        self.agent.set_controller(AgentController(self))
        
        # Central Widget & Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Toolbar
        self.create_toolbar()
        
        # Splitter for Sidebar + Tabs
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Sidebar (Initially Hidden)
        self.sidebar = Sidebar(self.data_manager, self, self.agent, self.voice_manager)
        self.sidebar.hide()
        self.splitter.addWidget(self.sidebar)
        
        # Tabs
        self.tabs = TabManager(self, profile=self.global_profile)
        self.splitter.addWidget(self.tabs)
        
        # Tab Health Monitor
        self.cleanup_proposal = None
        self.last_cleanup_prompt = 0
        self.tab_health_timer = QTimer()
        self.tab_health_timer.timeout.connect(self.monitor_tabs)
        self.tab_health_timer.start(10000) # Check every 10s
        
        # Set Splitter Factors to favor Web Content
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setCollapsible(0, False) # Can't fully collapse sidebar via dragging, button does it

        # Load initial tab
        self.add_new_tab(QUrl("xenit://newtab"), "New Tab")
        
        # Apply Styles for URL Bar uniqueness, reusing pill aesthetic
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 18px; /* Pill */
                padding: 10px 20px;
                color: #FAFAFA;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
                background-color: #09090b;
            }
        """)

    def monitor_tabs(self):
        import time
        if time.time() - self.last_cleanup_prompt < 300: # Don't bug more than once every 5 mins
            return
            
        count = self.tabs.count()
        if count < 4: return # Lower threshold for easier testing

        # Simple Clustering
        groups = {}
        for i in range(count):
            title = self.tabs.tabText(i)
            # Use main words > 3 chars
            words = [w.lower() for w in title.split() if len(w) > 3]
            for w in words:
                if w not in groups: groups[w] = []
                groups[w].append(i)
        
        # Check for heavy clusters
        for topic, indices in groups.items():
            if len(indices) >= 4: # Overload Threshold
                # Found overload
                titles = [self.tabs.tabText(i) for i in indices]
                self.cleanup_proposal = {"topic": topic, "indices": indices, "titles": titles}
                self.last_cleanup_prompt = time.time()
                
                msg = f"I noticed you have {len(indices)} tabs about '{topic}'. Want me to summarize them and close the extras? (Reply 'Yes' or 'Do it')"
                
                # Auto-open sidebar if hidden so user sees the help
                if not self.sidebar.isVisible():
                    self.sidebar.show()
                # Ensure AI tab is shown
                self.sidebar.show_ai_tab()
                
                self.sidebar.add_ai_message(msg)
                self.sidebar.show_ai_tab()
                
                self.sidebar.add_ai_message(msg)
                break

    def monitor_burnout(self):
        import time
        current_time = time.time()
        
        # 1. Check Continuous Usage
        # Threshold: 2 hours (7200s) of continuous work without a break
        # We assume a break happens if the window is minimized or idle (simplified here as raw uptime)
        
        work_duration = current_time - self.last_break_time
        
        if work_duration > 7200: # 2 Hours
            self.trigger_burnout_alert("Time for a break? You've been active for 2 hours.")
            return

        # 2. Check Context (Stress Scoring)
        try:
            current_url = self.tabs.currentWidget().url().toString().lower()
            current_title = self.tabs.currentWidget().title().lower()
            
            # Score for Work URL
            if any(k in current_url for k in self.burnout_keywords):
                self.stress_score += 1
            elif any(k in current_title for k in self.burnout_keywords):
                self.stress_score += 1
                
            # Score for Stress Search
            if "google.com" in current_url:
                 if any(s in current_url for s in self.stress_search_terms):
                     self.stress_score += 5 # Major spike for stress search
            
            # Decay (Recover slightly if doing nothing)
            if self.stress_score > 0:
                self.stress_score -= 0.5 
                
            # Threshold Check
            if self.stress_score > 20: # Arbitrary threshold for "High Stress"
                self.trigger_burnout_alert("🧠 High Mental Load Detected. Take a breather.")
                self.stress_score = 0 # Reset after alert
        except:
            pass
            
    def trigger_burnout_alert(self, msg):
        import time
        self.last_break_time = time.time() # Reset timer
        print(f"XeNit Burnout Alert: {msg}")
        self.emotion_popup.show_break_alert(msg)

    def create_toolbar(self):
        # Container for the floating effect
        self.toolbar_container = QWidget()
        self.toolbar_container.setFixedHeight(60) # Fixed height for consistency
        self.toolbar_container.setStyleSheet("""
            QWidget {
                background-color: #18181b; 
                border: 1px solid #27272a; 
                border-radius: 16px;
            }
        """)
        
        # Shadow for Floating Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 180)) # Darker shadow
        self.toolbar_container.setGraphicsEffect(shadow)

        self.tb_layout = QHBoxLayout(self.toolbar_container)
        self.tb_layout.setContentsMargins(15, 5, 15, 5) # Tighter vertical margins
        self.tb_layout.setSpacing(10)
        
        # Common Button Style with Neon Glow on Hover
        btn_style = """
            QPushButton { 
                background: transparent; 
                border-radius: 10px; 
                font-size: 16px; 
                color: #A1A1AA; 
                border: none;
            }
            QPushButton:hover { 
                background: rgba(0, 240, 255, 0.08); 
                color: #00F0FF; 
            }
            QPushButton:pressed {
                background: rgba(0, 240, 255, 0.15);
            }
        """

        # Navigation
        self.back_btn = QPushButton("←")
        self.fwd_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        
        for btn in [self.back_btn, self.fwd_btn, self.reload_btn]:
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(btn_style)
        
        self.back_btn.clicked.connect(lambda: self.tabs.currentWidget().back())
        self.fwd_btn.clicked.connect(lambda: self.tabs.currentWidget().forward())
        self.reload_btn.clicked.connect(lambda: self.tabs.currentWidget().reload())

        # Removed Library/Sidebar button as requested
        # self.tb_layout.addWidget(self.lib_btn) 
        
        self.tb_layout.addWidget(self.back_btn)
        self.tb_layout.addWidget(self.fwd_btn)
        self.tb_layout.addWidget(self.reload_btn)
        
        # URL Bar (Pill Shape)
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        # Style set in init for specificity, but layout added here
        self.tb_layout.addWidget(self.url_bar)
        
        # Custom AI Button
        self.ai_btn = QPushButton("✨") # Sparkle icon for AI
        self.ai_btn.setFixedSize(36, 36)
        # Make AI button stand out
        self.ai_btn.setStyleSheet("""
            QPushButton { 
                background: rgba(0, 240, 255, 0.1); 
                border-radius: 10px; 
                font-size: 18px; 
                color: #00F0FF; 
                border: 1px solid rgba(0, 240, 255, 0.3);
            }
            QPushButton:hover { 
                background: rgba(0, 240, 255, 0.2); 
                color: #FFFFFF; 
                border: 1px solid #00F0FF;
            }
            QPushButton:pressed {
                background: rgba(0, 240, 255, 0.3);
            }
        """)
        self.ai_btn.clicked.connect(self.open_ai_agent)
        self.tb_layout.addWidget(self.ai_btn)

        # Menu Button (Right)
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.setStyleSheet(btn_style)
        self.menu_btn.clicked.connect(self.show_menu)
        self.tb_layout.addWidget(self.menu_btn)
        
        self.main_layout.addWidget(self.toolbar_container)

    def open_ai_agent(self):
        if not self.sidebar.isVisible():
            self.sidebar.show()
        self.sidebar.show_ai_tab()

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def add_new_tab(self, qurl=None, label="New Tab"):
        # Apply Dot Trick globally to ALL new tabs (AI, Links, User)
        if qurl and isinstance(qurl, QUrl):
             host = qurl.host().lower()
             if "youtube.com" in host and not host.endswith("."):
                 new_host = host.replace("youtube.com", "youtube.com.")
                 qurl.setHost(new_host)
                 print(f"XeNit AdBlock: Applied Dot Trick (Global) -> {qurl.toString()}")
        
        browser = self.tabs.add_new_tab(qurl, label)
        
        # Connect Emotion Signal
        if hasattr(browser, 'emotion_detected'):
            browser.emotion_detected.connect(self.on_emotion_detected)
            
        return browser
        
    def on_emotion_detected(self, result, text):
        # Determine Risk Level
        risk = "Low"
        if result.confidence > 0.8: risk = "Medium"
        if result.is_crisis: risk = "CRITICAL"
        elif result.mood == "distress" and result.confidence > 0.6: risk = "High"
        elif "anger" in result.matched_keywords: risk = "High"
        
        try:
            with open("emotion_debug.log", "a", encoding="utf-8") as f:
                f.write(f"UI TRIGGER: {result.mood} ({risk}) - {result.matched_keywords}\n")
        except: pass
        
        print(f"XeNit UI: Showing Emotion Popup -> {result.mood} ({risk})")
        
        # 1. Show Immediate Emotion Alert
        self.emotion_popup.show_emotion(result.mood.title(), risk)
        
        # 1.5 Track Emotion History & Check for Fight Pattern
        import time
        current_time = time.time()
        self.emotion_history.append((current_time, result.mood, risk))
        
        # Prune old events (> 60 seconds)
        self.emotion_history = [e for e in self.emotion_history if current_time - e[0] < 60]
        
        # Check for Fight Pattern (Rapid Anger)
        anger_count = sum(1 for e in self.emotion_history if e[1] in ["anger", "crisis"] or e[2] in ["High", "CRITICAL"])
        
        if anger_count >= 3:
            print("XeNit: 🔥 FIGHT DETECTION TRIGGERED")
            self.emotion_popup.show_fight_alert()
            self.emotion_history.clear() # Reset after trigger to avoid spam
        if anger_count >= 3:
            print("XeNit: 🔥 FIGHT DETECTION TRIGGERED")
            self.emotion_popup.show_fight_alert()
            self.emotion_history.clear() # Reset after trigger
            
            # Connect "Calm Down" button
            try: self.emotion_popup.improve_btn.clicked.disconnect()
            except: pass
            try: self.emotion_popup.send_anyway_btn.clicked.disconnect()
            except: pass
            
            self.emotion_popup.improve_btn.clicked.connect(lambda: self.start_calm_worker(text))
            self.emotion_popup.send_anyway_btn.clicked.connect(self.emotion_popup.hide_anim)
            
            return # Skip other logic
        
        # 2. Check for Hurt Alert (Toxic/High Risk)
        is_hurtful = risk in ["High", "CRITICAL"] or result.mood in ["anger", "disgust", "crisis"]
        
        if is_hurtful:
            # 🚨 Show Hurt Alert
            self.emotion_popup.show_hurt_alert()
            
            # Connect Buttons
            try: self.emotion_popup.improve_btn.clicked.disconnect()
            except: pass
            try: self.emotion_popup.send_anyway_btn.clicked.disconnect()
            except: pass
            
            # Improve -> Rewrite & Auto-Copy
            # Use a helper to capture current relationship selection
            def handle_improve():
                rel = self.emotion_popup.rel_selector.currentText()
                self.trigger_rewrite(text, result.mood, rel)

            self.emotion_popup.improve_btn.clicked.connect(handle_improve)
            
            # Send Anyway -> Dismiss
            self.emotion_popup.send_anyway_btn.clicked.connect(self.emotion_popup.hide_anim)

        elif risk == "Medium" or result.mood in ["distress", "sadness"]:
            # ✨ Standard Auto-Copy Flow (for non-toxic but negative content)
            self.trigger_rewrite(text, result.mood)

    def trigger_rewrite(self, text, emotion, relationship="Friend"):
        # Run in Thread to avoid freezing UI
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class RewriteWorker(QThread):
            finished = pyqtSignal(str)
            def __init__(self, agent, text, emotion, relationship, mode="rewrite"):
                super().__init__()
                self.agent = agent
                self.text = text
                self.emotion = emotion
                self.relationship = relationship
                self.mode = mode
                
            def run(self):
                if self.mode == "rewrite":
                    suggestion = self.agent.rewrite_message(self.text, self.emotion, self.relationship)
                elif self.mode == "calm":
                    suggestion = self.agent.generate_calming_response(self.text)
                self.finished.emit(suggestion)
        
        self.worker = RewriteWorker(self.agent, text, emotion, relationship)
        self.worker.finished.connect(lambda suggestion: self.show_suggestion_ui(suggestion))
        self.worker.start()

    def trigger_calm_response(self, text):
        # Re-use worker with "calm" mode
        self.trigger_rewrite(text, "anger", relationship="Friend") # Mode override happens in worker
        # Wait, I need to pass mode. Let's refactor trigger_rewrite slightly or just make a new one.
        # Quickest way: Use the Worker modification above but I need to pass 'mode' param.
        # Let's clean up:
        pass 

    def start_calm_worker(self, text):
         # Run in Thread to avoid freezing UI
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class CalmWorker(QThread):
            finished = pyqtSignal(str)
            def __init__(self, agent, text):
                super().__init__()
                self.agent = agent
                self.text = text
            def run(self):
                suggestion = self.agent.generate_calming_response(self.text)
                self.finished.emit(suggestion)
        
        self.worker = CalmWorker(self.agent, text)
        self.worker.finished.connect(lambda suggestion: self.show_suggestion_ui(suggestion))
        self.worker.start()

    def show_suggestion_ui(self, suggestion):
        if suggestion:
            self.emotion_popup.show_suggestion(suggestion)
            self.emotion_popup.btn_widget.hide() # Hide buttons if they were showing for Hurt Alert
            self.emotion_popup.rel_selector.hide() # Hide selector
            
            # Auto-Copy to Clipboard
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(suggestion)
            print(f"XeNit: Copied suggestion to clipboard: {suggestion[:30]}...")

    def go_home(self):
        self.tabs.currentWidget().setUrl(QUrl("xenit://newtab"))

    def navigate_to_url(self):
        text = self.url_bar.text()
        if not text:
            return
            
        url = QUrl(text)
        if url.scheme() == "":
            if "." in text:
                url.setScheme("http")
            else:
                # Search
                url = QUrl(f"https://www.google.com/search?q={text}")
        
        # YouTube "Dot Trick" for Ad Blocking
        host = url.host().lower()
        if "youtube.com" in host and not host.endswith("."):
            new_host = host.replace("youtube.com", "youtube.com.")
            url.setHost(new_host)
            print(f"XeNit AdBlock: Applied Dot Trick (Nav) -> {url.toString()}")
        
        self.tabs.currentWidget().setUrl(url)
        
        # Check for Emotional Distress in Search
        if url.host() == "www.google.com" and "search" in url.path():
            # Extract query from URL is hard reliably here due to encoding, so use 'text' input
            # If the user typed "I feel lonely" into the URL bar, 'text' is that string.
            lower_text = text.lower()
            
            # Helper to check if any keyword from any category is present
            detected_category = None
            for category, keywords in self.emotional_keywords.items():
                if any(k in lower_text for k in keywords):
                    detected_category = category
                    break
            
            if detected_category:
                print(f"XeNit: Emotional Search Detected ({detected_category}) -> {lower_text}")
                # Trigger Sidebar Logic
                self.trigger_emotional_support(lower_text)

    def trigger_emotional_support(self, query):
        if self.sidebar.isVisible() == False:
            self.sidebar.show()
        self.sidebar.show_ai_tab()
        
        # Show a "Thinking..." or "Connecting..." state
        self.sidebar.add_ai_message("💙 I hear you. Let me find some support for you...")
        
        # Run AI in background
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class SupportWorker(QThread):
            finished = pyqtSignal(str)
            execute_action = pyqtSignal(str, str) # action, param
            
            def __init__(self, agent, query):
                super().__init__()
                self.agent = agent
                self.query = query
                
            def run(self):
                # We need to capture the response AND any side-effects (actions)
                # But AIAgent._process_actions runs immediately. 
                # We must modify AIAgent to return actions or handle them via callback.
                # For now, let's Monkey Patch the controller's methods to emit signals instead of running locally
                
                # ...Wait, better approach: 
                # Let AIAgent return the raw response, and we parse actions here in the main thread?
                # No, AIAgent logic is encapsulated.
                
                # Best approach: Give Agent a "SignalController" that emits signals
                # But Agent is shared.
                
                # Hack for stability: 
                # 1. Get raw text response
                # 2. Emit text
                # 3. Parse actions in MAIN THREAD (in finished slot)
                
                # To do this, we call a modified get_emotional_support that DOES NOT process actions
                pass # See below for implementation
                
                # Re-implementing get_emotional_support logic locally to detach side effects
                # checking agent presence
                if not self.agent.client:
                    self.finished.emit("I hear that you're going through something difficult. Please reach out to a professional.")
                    return

                system_prompt = """You are XeNit AI... (truncated for brevity, same as agent) ..."""
                # ... (System Prompt is large, duplicating it is bad) ...
                
                # Actually, let's just call the agent, but DISABLE the controller temporarily?
                # race condition.
                
                # Let's rely on the fact that `agent.get_emotional_support` calls `_process_actions`.
                # `_process_actions` uses `self.controller`.
                # If we temporarily swap `self.controller` with a thread-safe shim?
                
                original_controller = self.agent.controller
                
                class ThreadSafeShim:
                    def __init__(self, worker):
                        self.worker = worker
                    def open_url(self, url): self.worker.execute_action.emit("OPEN", url)
                    def play_music(self, query): self.worker.execute_action.emit("MUSIC", query)
                    def open_whatsapp(self, p): self.worker.execute_action.emit("WHATSAPP", p)
                    def auto_fill(self, p): self.worker.execute_action.emit("AUTOFILL", p)
                    def click_element(self, p): self.worker.execute_action.emit("CLICK", p)
                    def close_specific_tabs(self, p): self.worker.execute_action.emit("CLOSE_TABS", p)
                    
                self.agent.controller = ThreadSafeShim(self)
                
                try:
                    resp = self.agent.get_emotional_support(self.query)
                    self.finished.emit(resp)
                finally:
                    self.agent.controller = original_controller # Restore
        
        self.support_worker = SupportWorker(self.agent, query)
        self.support_worker.finished.connect(lambda resp: self.sidebar.add_ai_message(resp))
        
        # Connect the action signal to the REAL controller methods (Main Thread)
        def handle_action(action, param):
            print(f"XeNit MainThread Action: {action} -> {param}")
            if action == "OPEN": self.agent.controller.open_url(param)
            elif action == "MUSIC": self.agent.controller.play_music(param)
            elif action == "WHATSAPP": self.agent.controller.open_whatsapp(param)
            # Add others if needed
            
        self.support_worker.execute_action.connect(handle_action)
        self.support_worker.start()

    def update_url_bar(self, qurl, browser=None):
        if not hasattr(self, 'tabs') or browser != self.tabs.currentWidget():
            return

        if qurl.scheme() == "xenit":
            self.url_bar.setText("")
            self.url_bar.setPlaceholderText("Search the future...")
        else:
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

        # History Tracking
        if qurl.scheme() in ["http", "https"]:
            self.data_manager.add_history_item(browser.title(), qurl.toString())
        
        # Medical Safety Check on search pages
        self._check_medical_safety(qurl, browser)

    def _check_medical_safety(self, qurl, browser):
        """Checks if a URL is a health-related search and shows safety warnings."""
        if not browser:
            return
        
        url_str = qurl.toString().lower()
        if url_str == "about:blank" or url_str == "xenit://newtab":
            return

        # 1. Search Engine Check (Symptom Warning)
        search_query = None
        import urllib.parse as urlparse
        try:
            parsed = urlparse.urlparse(url_str)
            params = urlparse.parse_qs(parsed.query)
            
            # Google, Bing, DuckDuckGo, Yahoo
            if any(engine in url_str for engine in ["google.com/search", "bing.com/search", "duckduckgo.com", "search.yahoo.com"]):
                search_query = params.get("q", params.get("p", [None]))[0]
                
            if search_query:
                # Check against symptom database
                warning = check_health_search(search_query)
                if warning:
                    print(f"XeNit Safety: Detected '{warning['symptom']}' in search: {search_query}")
                    js_code = get_safety_banner_js(warning)
                    self._inject_safety_js(browser, js_code)
                    return # Don't show double warnings (search + untrusted)
        except Exception as e:
            print(f"XeNit Safety Error (Search): {e}")

        # 2. Untrusted Site Check (Domain Warning)
        try:
            untrusted = check_untrusted_medical_site(url_str)
            if untrusted:
                print(f"XeNit Safety: Untrusted health site detected: {qurl.host()}")
                trust_js = get_untrusted_site_banner_js(untrusted)
                self._inject_safety_js(browser, trust_js)
        except Exception as e:
            print(f"XeNit Safety Error (Site): {e}")

    def _inject_safety_js(self, browser, js_code):
        """Helper to inject JS safely whether loading or loaded."""
        
        def run_js():
            print("XeNit Safety: Injecting Warning Banner...")
            # We use a slight delay to ensure DOM is ready even if 'loadFinished' just fired
            browser.page().runJavaScript(f"setTimeout(function() {{ {js_code} }}, 1000);")

        if browser.progress() == 100:
            run_js()
        else:
            # Connect to single shot
            connection = None
            def on_loaded(ok):
                if ok: run_js()
                try:
                    if connection: browser.loadFinished.disconnect(connection)
                except: pass
            
            connection = browser.loadFinished.connect(on_loaded)

    def show_menu(self):
        menu = CustomMenu(self)
        
        # Connect actions
        menu.actions()[0].triggered.connect(self.show_sign_in) # Sign In is first action
        
        menu.new_tab_action.triggered.connect(lambda: self.add_new_tab())
        menu.new_window_action.triggered.connect(self.open_new_window)
        
        menu.history_action.triggered.connect(self.open_history)
        menu.bookmarks_action.triggered.connect(self.open_bookmarks)
        menu.downloads_action.triggered.connect(self.open_downloads)
        
        menu.settings_action.triggered.connect(self.open_settings)
        menu.help_action.triggered.connect(self.open_help)
        menu.exit_action.triggered.connect(self.close)
        
        # Show relative to button
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def open_new_window(self):
        # Create a new instance of BrowserWindow
        new_win = BrowserWindow()
        new_win.show()
        # Keep reference in a list on the main app if needed, 
        # normally purely local variable in Qt slots might get GC'd unless parented or explicitly referenced.
        # But for Top Level widgets .show() usually keeps them alive until closed if they have no parent.
        # To be safe, let's assume the main loop handles it, or we can add to a global list if tricky.
        pass

    def open_history(self):
        dlg = HistoryDialog(self)
        dlg.exec()

    def open_bookmarks(self):
        dlg = BookmarksDialog(self)
        dlg.exec()
        
    def open_downloads(self):
        dlg = DownloadsDialog(self)
        dlg.exec()

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        
    def open_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def show_sign_in(self):
        dlg = SignInDialog(self)
        dlg.exec()
