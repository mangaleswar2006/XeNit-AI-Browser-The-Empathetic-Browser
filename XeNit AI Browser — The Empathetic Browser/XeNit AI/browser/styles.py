
# Dark, Futuristic, Glassmorphism Theme (XeNit Ultra)

THEME_COLORS = {
    "background": "#09090b",       # Deepest Navy/Almos Black
    "background_alt": "#18181b",   # Zinc-900
    "text": "#FAFAFA",             # Zinc-50
    "accent": "#00F0FF",           # Cyberpunk Cyan
    "accent_hover": "#00B8E6",
    "secondary_accent": "#7000FF", # Electric Purple
    "danger": "#FF2A6D",           # Neon Red
    "border": "#27272a"            # Zinc-800
}

GLOBAL_STYLES = """
QMainWindow {
    background-color: #09090b;
    color: #FAFAFA;
}

QWidget {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    color: #FAFAFA;
}

/* Custom Scrollbar - Minimal */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #27272a;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* Tooltips */
QToolTip {
    background-color: #18181b;
    color: #FAFAFA;
    border: 1px solid #3f3f46;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}

/* Menu */
QMenu {
    background-color: #18181b; /* Zinc-900 */
    border: 1px solid #27272a;
    border-radius: 10px;
    padding: 5px;
}
QMenu::item {
    padding: 8px 20px;
    border-radius: 6px;
    color: #FAFAFA;
}
QMenu::item:selected {
    background-color: #27272a;
    color: #00F0FF;
}
"""
