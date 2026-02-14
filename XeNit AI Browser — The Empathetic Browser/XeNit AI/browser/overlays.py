from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen

class EmotionNotification(QWidget):
    def __init__(self, parent=None):
        # DETACH from parent to ensure top-level mouse handling
        super().__init__(None) 
        self.main_window = parent 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedSize(320, 100)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_label = QLabel("Emotion Detected")
        self.title_label.setStyleSheet("color: #FAFAFA; font-weight: bold; font-size: 14px; font-family: 'Segoe UI';")
        
        self.msg_label = QLabel("Analyzing...")
        self.msg_label.setStyleSheet("color: #A1A1AA; font-size: 12px; font-family: 'Segoe UI';")
        self.msg_label.setWordWrap(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.msg_label)
        
        
        # Suggestion UI (Hidden by Default)
        self.suggestion_label = QLabel("")
        self.suggestion_label.setStyleSheet("color: #E4E4E7; font-size: 11px; font-style: italic; margin-top: 5px;")
        self.suggestion_label.setWordWrap(True)
        self.suggestion_label.hide()
        layout.addWidget(self.suggestion_label)
        
        self.suggestion_label.hide()
        layout.addWidget(self.suggestion_label)
        
        # Relationship Selector (Added)
        self.rel_selector = QComboBox()
        self.rel_selector.addItems(["Friend", "Partner", "Boss", "Family", "Teacher"])
        self.rel_selector.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rel_selector.setStyleSheet("""
            QComboBox {
                background-color: #27272A;
                color: #A1A1AA;
                border: 1px solid #52525B;
                border-radius: 4px;
                padding: 2px 5px;
                font-size: 11px;
                font-family: 'Segoe UI';
                min-height: 20px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #27272A;
                color: #E4E4E7;
                selection-background-color: #3B82F6;
            }
        """)
        self.rel_selector.hide()
        layout.addWidget(self.rel_selector)

        # Buttons (Hidden by default, used for Hurt Alert)
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0, 5, 0, 0)
        
        self.improve_btn = QPushButton("✨ Improve message")
        self.improve_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.improve_btn.setStyleSheet("""
            background-color: #EF4444; color: white; border-radius: 6px; padding: 6px; font-weight: bold;
        """)
        
        self.send_anyway_btn = QPushButton("Send anyway")
        self.send_anyway_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_anyway_btn.setStyleSheet("""
            background-color: transparent; color: #A1A1AA; border: 1px solid #52525B; border-radius: 6px; padding: 6px;
        """)
        
        self.btn_layout.addWidget(self.send_anyway_btn)
        self.btn_layout.addWidget(self.improve_btn)
        
        self.btn_widget = QWidget()
        self.btn_widget.setLayout(self.btn_layout)
        self.btn_widget.hide()
        layout.addWidget(self.btn_widget)
        
        # Opacity Effect for Animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Timer to auto-hide
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_anim)



    def paintEvent(self, event):
        # Manually draw the background to ensure hit-testing works
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Parse current logic (colors)
        # We need to store current colors/state for painting
        # But for now, let's use the colors set in show_emotion
        
        if hasattr(self, 'current_bg_color') and hasattr(self, 'current_border_color'):
            bg = QColor(self.current_bg_color)
            border = QColor(self.current_border_color)
            
            painter.setBrush(QBrush(bg))
            pen = QPen(border)
            pen.setWidth(1)
            painter.setPen(pen)
            
            # Main Rect
            painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 12, 12)
            
            # Draw Left Border Accent
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(3, 12, 3, self.height() - 12)

    def show_emotion(self, emotion, risk_level="Low"):
        # Reset Support UI
        self.suggestion_label.hide()
        self.btn_widget.hide()
        self.rel_selector.hide()
        self.setFixedHeight(100)
        
        # Color Coding based on Emotion/Risk
        self.current_border_color = "#00F0FF" # Default Cyan
        self.current_bg_color = QColor(24, 24, 27, 245) # rgba(24, 24, 27, 0.95)
        icon = "🤖"
        
        e_lower = emotion.lower()
        
        if "anger" in e_lower or "rage" in e_lower:
            self.current_border_color = "#FF2A6D" # Red/Pink
            icon = "😠"
        elif "sad" in e_lower or "depress" in e_lower:
            self.current_border_color = "#3B82F6" # Blue
            icon = "😢"
        elif "love" in e_lower or "happy" in e_lower or "joy" in e_lower:
            self.current_border_color = "#10B981" # Green
            icon = "❤️"
        elif "stress" in e_lower or "anxi" in e_lower:
            self.current_border_color = "#F59E0B" # Orange
            icon = "😰"
        elif "jealous" in e_lower:
            self.current_border_color = "#8B5CF6" # Purple
            icon = "😒"
            
        if risk_level == "High" or risk_level == "CRITICAL":
             self.current_border_color = "#EF4444" # Bright Red
             icon = "🚨"

        # Apply styles only to child widgets (Labels, Buttons)
        # Removing QWidget background style to rely on paintEvent
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_border_color};
                color: #000;
                border: none;
                border-radius: 6px;
                padding: 5px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                background-color: #FAFAFA;
            }}
            QPushButton#dismiss {{
                background-color: transparent;
                color: #A1A1AA;
                border: 1px solid #3F3F46;
            }}
            QPushButton#dismiss:hover {{
                background-color: #3F3F46;
                color: #FFF;
            }}
        """)
        
        self.title_label.setText(f"{icon} Emotion Detected: {emotion}")
        self.msg_label.setText(f"Risk Level: {risk_level}")
        
        # Position: Bottom Right of Parent Window
        if self.main_window:
            parent_rect = self.main_window.geometry()
            # Calculate absolute position since we are top-level now
            global_pos = self.main_window.mapToGlobal(QPoint(0,0))
            
            x = global_pos.x() + parent_rect.width() - self.width() - 20
            y = global_pos.y() + parent_rect.height() - self.height() - 80 # Above status bar area
            self.move(x, y)
            
        self.show()
        self.fade_in()
        self.repaint() # Force repaint with new colors
        
        # Auto hide after 5 seconds if no interaction
        self.hide_timer.start(5000)

    def show_hurt_alert(self):
        self.hide_timer.stop()
        
        # Style for Toxicity Blocker
        self.title_label.setText("🚫 Toxicity Detected")
        self.msg_label.setText("This could damage your relationship.")
        
        self.current_border_color = "#EF4444" # Red
        self.current_bg_color = QColor(40, 0, 0, 245) # Dark Red Background
        
        # Show Buttons
        self.suggestion_label.hide()
        self.btn_widget.show()
        self.rel_selector.show() # Show selector
        print("XeNit UI: Showing Relationship Selector")
        
        self.setFixedHeight(200) # Increased height for selector
        self.repaint()
        
        # Position
        if self.main_window:
            parent_rect = self.main_window.geometry()
            global_pos = self.main_window.mapToGlobal(QPoint(0,0))
            x = global_pos.x() + parent_rect.width() - self.width() - 20
            y = global_pos.y() + parent_rect.height() - 200 - 80
            self.move(x, y)
        
        self.show()
        self.fade_in()

    def show_break_alert(self, message):
        self.hide_timer.stop()
        
        # Style for Burnout Prevention
        self.title_label.setText("🧠 Brain Overload Detected")
        self.msg_label.setText(message)
        
        self.current_border_color = "#10B981" # Green (Calming)
        self.current_bg_color = QColor(6, 78, 59, 245) # Dark Green
        
        # Show Buttons (Reuse improvement buttons for now, or add specific ones)
        # Check if we need to remove old connections to avoid double actions
        try: self.improve_btn.clicked.disconnect()
        except: pass
        try: self.send_anyway_btn.clicked.disconnect()
        except: pass
        
        self.improve_btn.setText("🍵 Take a Breath")
        self.improve_btn.setStyleSheet("""
            background-color: #10B981; color: white; border-radius: 6px; padding: 6px; font-weight: bold;
        """)
        
        self.send_anyway_btn.setText("5 More Minutes")
        
        # Connect Actions
        self.improve_btn.clicked.connect(self.start_break_mode)
        self.send_anyway_btn.clicked.connect(self.hide_anim)
        
        self.suggestion_label.hide()
        self.btn_widget.show()
        self.rel_selector.hide()
        
        self.setFixedHeight(160)
        self.repaint()
        
        # Position
        if self.main_window:
            parent_rect = self.main_window.geometry()
            global_pos = self.main_window.mapToGlobal(QPoint(0,0))
            x = global_pos.x() + parent_rect.width() - self.width() - 20
            y = global_pos.y() + parent_rect.height() - 160 - 80
            self.move(x, y)
        
        self.show()
        self.fade_in()

    def start_break_mode(self):
        self.hide_anim()
        # Open a relaxing tab via the main window
        if self.main_window:
            self.main_window.add_new_tab(QUrl("https://www.calm.com/breathe"), "Breathe")

    def show_suggestion(self, rewritten_text):
        self.hide_timer.stop() # Stop auto-hide so user can read
        
        self.suggestion_label.setText(f"✨ <b>Suggestion:</b> \"{rewritten_text}\"<br><br><i>(Copied to Clipboard)</i>")
        self.suggestion_label.show()
        self.rel_selector.hide() # Hide when done
        
        # Animate Height Expansion
        self.anim_expand = QPropertyAnimation(self, b"size")
        self.anim_expand.setDuration(300)
        self.anim_expand.setStartValue(QSize(320, 100))
        self.anim_expand.setEndValue(QSize(320, 160)) # Expand height (smaller than before since no buttons)
        self.anim_expand.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_expand.start()
        
        # Adjust position upwards to keep bottom aligned
        if self.main_window:
             parent_rect = self.main_window.geometry()
             global_pos = self.main_window.mapToGlobal(QPoint(0,0))
             
             x = global_pos.x() + parent_rect.width() - self.width() - 20
             y = global_pos.y() + parent_rect.height() - 160 - 80
             self.move(x, y)
             
        # Auto-hide after 8 seconds (give time to read/paste)
        self.hide_timer.start(8000)

    def fade_in(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def hide_anim(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.finished.connect(self.hide)
        self.anim.start()

