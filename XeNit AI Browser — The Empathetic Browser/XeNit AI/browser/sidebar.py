from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                             QTabWidget, QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon

class AgentChatWidget(QWidget):
    voice_recognized = pyqtSignal(str)
    voice_error = pyqtSignal(str)

    def __init__(self, agent, browser_window, voice_manager=None):
        super().__init__()
        self.agent = agent
        self.browser_window = browser_window
        self.voice_manager = voice_manager
        
        # Connect signals for thread safety
        self.voice_recognized.connect(self.handle_voice_text)
        self.voice_error.connect(self.handle_voice_error)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Mood Indicator Bar
        self.mood_label = QLabel("🟢 Relaxed")
        self.mood_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mood_label.setStyleSheet("""
            QLabel {
                background-color: #1a2e1a;
                color: #4ade80;
                border-radius: 8px;
                padding: 6px;
                font-size: 11px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
        """)
        layout.addWidget(self.mood_label)
        
        # Chat History
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #18181b;
                color: #FAFAFA;
                border: 1px solid #27272a;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Segoe UI';
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask XeNit AI...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 15px;
                padding: 8px 15px;
                color: #FAFAFA;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        # Mic Button
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(30, 30)
        self.mic_btn.setStyleSheet("background: transparent; color: #FAFAFA; border: none;")
        self.mic_btn.clicked.connect(self.toggle_voice)
        
        send_btn = QPushButton("➤")
        send_btn.setFixedSize(30, 30)
        send_btn.setStyleSheet("background: transparent; color: #00F0FF; font-weight: bold; border: none;")
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.mic_btn)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)
        
        # Welcome Message
        self.chat_display.append("**XeNit AI:** Hello! I'm your health & wellness assistant. Type or speak — I'm here to help. 💙")

    def toggle_voice(self):
        if not self.voice_manager or not self.voice_manager.enabled:
             self.add_message("⚠️ Voice control not available (Libs missing).", is_user=False)
             return

        if self.voice_manager.is_listening:
             return 

        self.mic_btn.setStyleSheet("background: transparent; color: #FF2A6D; border: 1px solid #FF2A6D; border-radius: 15px;")
        self.input_field.setPlaceholderText("Listening...")
        
        # Start listening in bg
        self.voice_manager.listen_once(
            callback_success=lambda text: self.voice_recognized.emit(text),
            callback_error=lambda msg: self.voice_error.emit(msg)
        )

    def handle_voice_text(self, text):
        self.mic_btn.setStyleSheet("background: transparent; color: #FAFAFA; border: none;")
        self.input_field.setPlaceholderText("Ask XeNit AI...")
        if text:
            self.input_field.setText(text)
            self.send_message(via_voice=True)

    def handle_voice_error(self, msg):
        self.mic_btn.setStyleSheet("background: transparent; color: #FAFAFA; border: none;")
        self.input_field.setPlaceholderText("Ask XeNit AI...")
        self.add_message(f"⚠️ Voice Error: {msg}", is_user=False)

    def send_message(self, via_voice=False):
        text = self.input_field.text().strip()
        if not text:
            return
            
        # Display user message
        self.add_message(text, is_user=True)
        self.input_field.clear()
        
        # Get Context from Browser
        context = self.get_browser_context()
        if hasattr(self.browser_window, 'cleanup_proposal'):
            context['cleanup_proposal'] = self.browser_window.cleanup_proposal
        
        # Get Agent Response
        response = self.agent.chat(text, context)
        self.add_message(response, is_user=False)
        
        # Update Mood Indicator based on detected emotion
        self._update_mood_indicator()
        
        # Speak back if user spoke
        if via_voice and self.voice_manager:
            self.voice_manager.speak(response)

        # Parse and Show Smart Reply Chips
        import re
        reply_pattern = r"\[\[REPLY:(.*?)\]\]"
        matches = re.findall(reply_pattern, response)
        
        if matches:
            self.show_reply_chips(matches)

    def show_reply_chips(self, replies):
        # Create a container for chips if not exists
        if not hasattr(self, 'chip_container'):
            self.chip_container = QWidget()
            self.chip_layout = QHBoxLayout(self.chip_container)
            self.chip_layout.setContentsMargins(0, 5, 0, 5)
            self.chip_layout.setSpacing(5)
            # Add to main layout above input
            # Find index of input_layout to insert before it
            self.layout().insertWidget(self.layout().count() - 2, self.chip_container)
        
        # Clear old chips
        while self.chip_layout.count():
            child = self.chip_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.chip_container.show()
                
        for reply_text in replies:
            reply_text = reply_text.strip()
            chip = QPushButton(reply_text)
            chip.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a2e;
                    color: #60a5fa;
                    border: 1px solid #3b82f6;
                    border-radius: 12px;
                    padding: 5px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #3b82f6;
                    color: white;
                }
            """)
            chip.clicked.connect(lambda checked, t=reply_text: self.on_chip_clicked(t))
            self.chip_layout.addWidget(chip)
            
    def on_chip_clicked(self, text):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Feedback
        self.input_field.setText(f"Copied: '{text}'")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self.input_field.clear)
    
    def add_message(self, text, is_user=False):
        # Prevent "AI: AI: response" duplication if agent adds prefix
        prefix = "**You:**" if is_user else "**AI:**"
        if text.startswith("**AI:**") or text.startswith("**XeNit:**"):
            prefix = "" 
            
        self.chat_display.append(f"{prefix} {text}\n")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def _update_mood_indicator(self):
        """Updates the mood bar based on the agent's last emotion detection."""
        emotion = getattr(self.agent, 'last_emotion', None)
        if not emotion:
            return
        
        if emotion.is_crisis:
            self.mood_label.setText("🚨 Crisis Support Active")
            self.mood_label.setStyleSheet("""
                QLabel {
                    background-color: #3b1019;
                    color: #ff6b8a;
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                    border: 1px solid #ff2a6d;
                }
            """)
        elif emotion.needs_comfort:
            self.mood_label.setText("💙 Comfort + Support Mode")
            self.mood_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a2e;
                    color: #60a5fa;
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                    border: 1px solid #3b82f6;
                }
            """)
        elif emotion.mood == "positive":
            self.mood_label.setText("😊 Positive Vibes")
            self.mood_label.setStyleSheet("""
                QLabel {
                    background-color: #1a2e1a;
                    color: #4ade80;
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                }
            """)
        else:
            self.mood_label.setText("🟢 Relaxed")
            self.mood_label.setStyleSheet("""
                QLabel {
                    background-color: #1a2e1a;
                    color: #4ade80;
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                }
            """)

    def get_browser_context(self):
        # Retrieve current tab details
        current_browser = self.browser_window.tabs.currentWidget()
        if not current_browser:
            return None
            
        context = {
            "url": current_browser.url().toString(),
            "title": current_browser.title(),
            "text": "" # Will be populated if asynchronous fetching was easy.
        }
        
        if hasattr(current_browser, 'last_extracted_text'):
             context['text'] = current_browser.last_extracted_text
             
        return context

class Sidebar(QWidget):
    def __init__(self, data_manager, browser_window, agent=None, voice_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.browser_window = browser_window
        self.agent = agent
        self.voice_manager = voice_manager
        
        self.setFixedWidth(300)
        self.setStyleSheet("""
            QWidget {
                background-color: #09090b;
                border-right: 1px solid #27272a;
            }
            QTabWidget::pane {
                border: none;
                background: #09090b;
            }
            QTabBar::tab {
                background: #18181b;
                color: #71717a;
                padding: 10px;
                border: none;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #09090b;
                color: #00F0FF;
                border-bottom: 2px solid #00F0FF;
            }
            QListWidget {
                background-color: #09090b;
                border: none;
                outline: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px;
                color: #FAFAFA;
                border-radius: 8px;
                margin-bottom: 5px;
                background-color: #18181b;
                border: 1px solid #27272a;
            }
            QListWidget::item:hover {
                background-color: #27272a;
                border-color: #00F0FF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabs for History / Bookmarks / AI
        self.tabs = QTabWidget()
        
        # AI Agent Tab (First for visibility)
        if self.agent:
            self.ai_widget = AgentChatWidget(self.agent, self.browser_window, self.voice_manager)
            self.tabs.addTab(self.ai_widget, "AI Agent")
            
        # History Tab
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_item)
        self.tabs.addTab(self.history_list, "History")
        
        # Bookmarks Tab
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemClicked.connect(self.load_item)
        self.tabs.addTab(self.bookmarks_list, "Bookmarks")
        
        layout.addWidget(self.tabs)
        
        # Close Button (Bottom)
        close_layout = QHBoxLayout()
        close_layout.setContentsMargins(0, 5, 0, 10)
        
        self.close_btn = QPushButton("✕ Close Sidebar")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #52525b;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #ef4444; /* Red on hover */
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        
        close_layout.addStretch()
        close_layout.addWidget(self.close_btn)
        close_layout.addStretch()
        
        layout.addLayout(close_layout)
        
        self.refresh()

    def refresh(self):
        # Refresh History
        self.history_list.clear()
        history = self.data_manager.get_history()
        for item in history:
            # Format: Title (URL)
            display_text = f"{item.get('title', 'No Title')}\n{item.get('url', '')}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item.get('url'))
            self.history_list.addItem(list_item)
            
        # Refresh Bookmarks
        self.bookmarks_list.clear()
        bookmarks = self.data_manager.get_bookmarks()
        for item in bookmarks:
            display_text = f"{item.get('title', 'No Title')}\n{item.get('url', '')}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item.get('url'))
            self.bookmarks_list.addItem(list_item)

    def load_item(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            from PyQt6.QtCore import QUrl
            self.browser_window.add_new_tab(QUrl(url), label="Loading...")

    def show_ai_tab(self):
        if hasattr(self, 'ai_widget'):
            self.tabs.setCurrentWidget(self.ai_widget)

    def add_ai_message(self, text):
        if hasattr(self, 'ai_widget'):
            self.ai_widget.add_message(text, is_user=False)
