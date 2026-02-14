from PyQt6.QtWidgets import QMenu, QWidgetAction, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class CustomMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenu {
                background-color: #09090b;
                border: 1px solid #27272a;
                border-radius: 12px;
                padding: 8px;
                color: #FAFAFA;
            }
            QMenu::item {
                padding: 10px 25px;
                border-radius: 6px;
                margin: 2px 0px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 240, 255, 0.1);
                color: #00F0FF;
            }
            QMenu::separator {
                height: 1px;
                background: #27272a;
                margin: 5px 10px;
            }
        """)
        
        # Header (Sync/Profile)
        profile_action = QAction("👤 Sign In / Sync", self)
        self.addAction(profile_action)
        self.addSeparator()

        # Core Actions
        self.new_tab_action = QAction("New Tab (Ctrl+T)", self)
        self.new_window_action = QAction("New Window (Ctrl+N)", self)
        
        self.addAction(self.new_tab_action)
        self.addAction(self.new_window_action)
        self.addSeparator()
        
        # Lists
        self.history_action = QAction("History", self)
        self.bookmarks_action = QAction("Bookmarks", self)
        self.downloads_action = QAction("Downloads", self)
        
        self.addAction(self.history_action)
        self.addAction(self.bookmarks_action)
        self.addAction(self.downloads_action)
        self.addSeparator()
        
        # Tools
        self.settings_action = QAction("Settings", self)
        self.help_action = QAction("Help", self)
        self.exit_action = QAction("Exit", self)
        
        self.addAction(self.settings_action)
        self.addAction(self.help_action)
        self.addSeparator()
        self.addAction(self.exit_action)
