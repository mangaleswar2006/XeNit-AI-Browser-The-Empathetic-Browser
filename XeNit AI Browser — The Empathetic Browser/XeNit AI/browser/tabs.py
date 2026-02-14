from PyQt6.QtWidgets import QTabWidget, QTabBar, QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QIcon
from browser.engine import WebView
from browser.pages import get_new_tab_html
from functools import partial

class TabManager(QTabWidget):
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile
        self.setTabsClosable(False) # We are using custom buttons
        self.setMovable(True)
        self.setDocumentMode(True)
        self.currentChanged.connect(self.tab_changed)
        
        self.setStyleSheet("""
            QTabWidget::pane { 
                border: 0; 
                background: #09090b; 
            }
            QTabWidget::tab-bar {
                left: 10px; 
            }
            QTabBar::tab {
                background: transparent;
                color: #A1A1AA;
                padding: 8px 30px 8px 16px; /* Extra padding right for close button */
                border-radius: 8px;
                margin-right: 4px;
                min-width: 100px;
                max-width: 200px;
                border: 1px solid transparent;
            }
            QTabBar::tab:selected {
                background: #18181b;
                color: #FAFAFA;
                border: 1px solid #27272a;
                border-bottom: 1px solid #00F0FF; 
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255, 255, 255, 0.03);
                color: #FAFAFA;
            }
            /* Style the last tab (the '+' button) */
            QTabBar::tab:last {
                background: transparent;
                color: #00F0FF;
                min-width: 30px;
                max-width: 30px;
                padding: 0px;
                margin-left: 5px;
                border-radius: 15px; /* Circle */
                font-weight: bold;
                font-size: 16px;
            }
            QTabBar::tab:last:hover {
                background: rgba(0, 240, 255, 0.1);
            }
        """)
        
        # Add the plus button tab (dummy tab)
        self.plus_tab_widget = QWidget()
        
        # Block signals to prevent tab_changed from firing and creating an extra tab on startup
        self.blockSignals(True)
        i = self.addTab(self.plus_tab_widget, "+")
        self.blockSignals(False)
        
        # Hide the close button on the plus tab specifically
        self.tabBar().setTabButton(i, QTabBar.ButtonPosition.RightSide, None)
        self.tabBar().setTabButton(i, QTabBar.ButtonPosition.LeftSide, None)

    def add_new_tab(self, qurl=None, label="New Tab"):
        
        if qurl is None:
            qurl = QUrl("")
            
        browser = WebView(self.count(), self, profile=self.profile)
        
        # Insert before the last tab (the plus button)
        insert_index = max(0, self.count() - 1)
        
        i = self.insertTab(insert_index, browser, label)
        self.setCurrentIndex(i)
        
        # Create and set custom close button
        close_btn = QPushButton("✖")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setProperty("target_browser", browser) # robust binding
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #A1A1AA;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: rgba(255, 42, 109, 0.2);
                color: #FF2A6D;
            }
        """)
        
        close_btn.clicked.connect(self.on_close_click)
        
        self.tabBar().setTabButton(i, QTabBar.ButtonPosition.RightSide, close_btn)
        
        if qurl.toString() == "" or qurl.scheme() == "xenit":
            browser.setHtml(get_new_tab_html(), QUrl("xenit://newtab"))
        else:
            browser.load(qurl)
            
        browser.titleChanged.connect(lambda title: self.setTabText(self.indexOf(browser), title[:20]))
        browser.iconChanged.connect(lambda icon: self.setTabIcon(self.indexOf(browser), icon))
        browser.urlChanged.connect(lambda url: self.window().update_url_bar(url, browser))
        
        # Add fade-in animation for smoother transition
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        
        opacity_effect = QGraphicsOpacityEffect(browser)
        browser.setGraphicsEffect(opacity_effect)
        
        anim = QPropertyAnimation(opacity_effect, b"opacity")
        anim.setDuration(300) # 300ms fade in
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # CRITICAL FIX: Remove the effect after animation to restore hardware acceleration
        # Leaving QGraphicsOpacityEffect on a QWebEngineView causes heavy flickering/tearing
        def cleanup_effect():
            browser.setGraphicsEffect(None)
            
        anim.finished.connect(cleanup_effect)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        # Keep reference to animation to prevent garbage collection
        browser.fadeInAnim = anim
        
        return browser

    def on_close_click(self):
        btn = self.sender()
        if not btn:
            return
            
        browser = btn.property("target_browser")
        if browser:
            print(f"Closing tab for browser: {browser}")
            self.close_tab_by_widget(browser)

    def close_tab_by_widget(self, widget):
        index = self.indexOf(widget)
        # print(f"Found index {index} for widget {widget}")
        if index != -1:
            self.close_tab(index)

    def close_tab(self, index):
        # Don't allow closing the last tab (plus button)
        if index == self.count() - 1:
            return
            
        # Get the widget BEFORE removing it
        widget = self.widget(index)
        
        self.removeTab(index)
        
        # Explicitly delete the widget to stop audio/video and free memory
        if widget:
            widget.deleteLater()
        
        if self.count() == 1:
            self.add_new_tab()

    def tab_changed(self, index):
        # Check if the plus tab was clicked
        if index == self.count() - 1 and self.count() > 0:
            # Create new tab
            self.add_new_tab()
            return

        current_widget = self.currentWidget()
        if current_widget and isinstance(current_widget, WebView):
            if hasattr(self.window(), 'update_url_bar'):
                self.window().update_url_bar(current_widget.url(), current_widget)
