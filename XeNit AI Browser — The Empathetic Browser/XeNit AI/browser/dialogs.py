from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, 
                             QPushButton, QLineEdit, QCheckBox, QComboBox, QFormLayout, QWidget)
from PyQt6.QtCore import Qt, QSize
from browser.data_manager import DataManager

class BaseDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #09090b;
                border: 1px solid #27272a;
                color: #FAFAFA;
            }
            QLabel { color: #FAFAFA; font-size: 14px; }
            QListWidget {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 8px;
                color: #A1A1AA;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #27272a;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 240, 255, 0.1);
                color: #00F0FF;
            }
            QPushButton {
                background-color: #18181b;
                border: 1px solid #27272a;
                color: #FAFAFA;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(0, 240, 255, 0.1);
                border-color: #00F0FF;
                color: #00F0FF;
            }
            QLineEdit, QComboBox {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 4px;
                padding: 5px;
                color: #FAFAFA;
            }
        """)
        self.layout = QVBoxLayout(self)

class HistoryDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("History", parent)
        self.data_manager = DataManager()
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        self.load_history()
        
        self.list_widget.itemDoubleClicked.connect(self.open_url)
        
        btn = QPushButton("Clear History")
        btn.clicked.connect(self.clear_history)
        self.layout.addWidget(btn)

    def load_history(self):
        self.list_widget.clear()
        for item in self.data_manager.get_history():
            # item = {title, url, timestamp}
            display_text = f"{item.get('title', 'No Title')}\n{item.get('url', '')}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item.get('url'))
            self.list_widget.addItem(list_item)

    def open_url(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if hasattr(self.parent(), 'add_new_tab'):
            from PyQt6.QtCore import QUrl
            self.parent().add_new_tab(QUrl(url), "New Tab")
            self.close()

    def clear_history(self):
        self.data_manager.history = []
        self.data_manager.save_json([], self.data_manager.history_file)
        self.load_history()

class BookmarksDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Bookmarks", parent)
        self.data_manager = DataManager()
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        self.load_bookmarks()
        
        self.list_widget.itemDoubleClicked.connect(self.open_url)

    def load_bookmarks(self):
        self.list_widget.clear()
        for item in self.data_manager.get_bookmarks():
            display_text = f"{item.get('title', 'No Title')}\n{item.get('url', '')}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item.get('url'))
            self.list_widget.addItem(list_item)

    def open_url(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if hasattr(self.parent(), 'add_new_tab'):
            from PyQt6.QtCore import QUrl
            self.parent().add_new_tab(QUrl(url), "New Tab")
            self.close()

class DownloadsDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Downloads", parent)
        
        label = QLabel("No downloads yet.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        
        # Placeholder list
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

class SettingsDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        
        form_layout = QFormLayout()
        
        self.cb_adblock = QCheckBox("Enable AdBlock (Aggressive)")
        self.cb_adblock.setChecked(True)
        form_layout.addRow("Security:", self.cb_adblock)
        
        self.cb_darkmode = QCheckBox("Force Dark Mode")
        self.cb_darkmode.setChecked(True)
        form_layout.addRow("Appearance:", self.cb_darkmode)
        
        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "DuckDuckGo", "Bing", "Brave Search"])
        form_layout.addRow("Search Engine:", self.search_engine)
        
        container = QWidget()
        container.setLayout(form_layout)
        self.layout.addWidget(container)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.accept)
        self.layout.addWidget(save_btn)

class HelpDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Help / About", parent)
        self.resize(300, 200)
        
        label = QLabel("XeNit Browser v1.0")
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00F0FF;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        
        info = QLabel("Powered by PyQt6 & Python.\n\nCreated by Lucky.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(info)
        
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        self.layout.addWidget(btn)

class SignInDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Sign In / Sync", parent)
        self.resize(300, 250)
        
        self.layout.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        self.layout.addWidget(self.email)
        
        self.layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password)
        
        self.layout.addStretch()
        
        btn = QPushButton("Sign In")
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)
