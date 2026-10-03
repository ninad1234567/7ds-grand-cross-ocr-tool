# Entry point for 7DS Grand Cross Character & Attribute Snip-Capture App
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from main_window import MainWindow

def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setApplicationName("7DS Grand Cross Snip Capture")
    app.setOrganizationName("7DSGC")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
