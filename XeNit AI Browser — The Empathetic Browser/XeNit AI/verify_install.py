import sys
print("Python Executable:", sys.executable)
print("Path:", sys.path)
try:
    import PyQt6
    print("PyQt6 found at:", PyQt6.__file__)
    from PyQt6.QtWidgets import QApplication
    print("PyQt6.QtWidgets imported successfully")
except ImportError as e:
    print("Import Error:", e)
except Exception as e:
    print("Other Error:", e)
