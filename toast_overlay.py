# Non-Activating Overlay Toast for 7DS Grand Cross
import sys
import ctypes
from ctypes import wintypes
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont, QCursor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080

SW_SHOWNOACTIVATE = 4
HWND_TOPMOST = -1
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002

class ToastOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self.setFixedSize(420, 120)

        # Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(18, 12, 16, 12)
        self.main_layout.setSpacing(4)

        # Header bar with close button
        header_layout = QHBoxLayout()
        self.lbl_header = QLabel("⚔️ 7DS CHARACTER SAVED")
        self.lbl_header.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
        
        self.lbl_badge = QLabel("NEW")
        self.lbl_badge.setStyleSheet("background-color: #10b981; color: white; font-size: 9px; font-weight: bold; border-radius: 4px; padding: 2px 6px;")
        
        # Interactive Close Button (X)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #cbd5e1;
                border: none;
                border-radius: 11px;
                font-size: 11px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: #ffffff;
            }
        """)
        self.btn_close.clicked.connect(self.close_toast)

        header_layout.addWidget(self.lbl_header)
        header_layout.addWidget(self.lbl_badge)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_close)
        self.main_layout.addLayout(header_layout)

        # Character Name
        self.lbl_name = QLabel("Character Name")
        self.lbl_name.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
        self.lbl_name.setWordWrap(True)
        self.main_layout.addWidget(self.lbl_name)

        # Sub details
        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(8)

        self.lbl_attribute = QLabel("Attribute: Darkness")
        self.lbl_attribute.setStyleSheet("color: #c084fc; font-size: 12px; font-weight: bold;")
        
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        
        sub_layout.addWidget(self.lbl_attribute)
        sub_layout.addWidget(self.lbl_info)
        sub_layout.addStretch()
        self.main_layout.addLayout(sub_layout)

        # Animation
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.border_color = "#a855f7"

    def apply_windows_topmost_noactivate(self, x: int, y: int):
        if sys.platform == "win32":
            try:
                hwnd = int(self.winId())
                user32 = ctypes.windll.user32
                style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
                user32.SetWindowPos(hwnd, HWND_TOPMOST, x, y, self.width(), self.height(), SWP_SHOWWINDOW | SWP_NOACTIVATE)
                user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
                user32.BringWindowToTop(hwnd)
            except Exception:
                pass

    def show_character(self, char_data: dict, is_new: bool = True):
        """Displays toast popup for saved or already-existing character."""
        name = char_data.get("full_name") or char_data.get("name", "Unknown Character")
        attr_display = char_data.get("attribute_display") or char_data.get("attribute", "Unknown")
        attr_hex = char_data.get("attribute_hex", "#a855f7")
        race = char_data.get("race", "")
        cc = char_data.get("combat_class", "")

        self.lbl_name.setText(name)
        self.lbl_attribute.setText(f"● {attr_display}")
        self.lbl_attribute.setStyleSheet(f"color: {attr_hex}; font-size: 12px; font-weight: bold;")
        self.lbl_attribute.setVisible(True)

        if is_new:
            self.border_color = attr_hex
            self.lbl_header.setText("✨ CHARACTER SAVED")
            self.lbl_header.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
            self.lbl_badge.setText("SAVED")
            self.lbl_badge.setStyleSheet("background-color: #10b981; color: white; font-size: 9px; font-weight: bold; border-radius: 4px; padding: 2px 6px;")
            self.lbl_badge.setVisible(True)
            
            extras = []
            if race and race != "Unknown":
                extras.append(f"Race: {race}")
            if cc:
                extras.append(f"CC: {cc}")
            self.lbl_info.setText(" | ".join(extras) if extras else "Added to Character List")
            self.lbl_info.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        else:
            self.border_color = "#f59e0b" # Warning amber
            self.lbl_header.setText("⚠️ CHARACTER ALREADY EXISTS")
            self.lbl_header.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
            self.lbl_badge.setText("ALREADY IN LIST")
            self.lbl_badge.setStyleSheet("background-color: #d97706; color: white; font-size: 9px; font-weight: bold; border-radius: 4px; padding: 2px 6px;")
            self.lbl_badge.setVisible(True)
            self.lbl_info.setText("Duplicate skipped & not added again.")
            self.lbl_info.setStyleSheet("color: #fbbf24; font-size: 11px; font-style: italic;")

        self._trigger_display()

    def show_no_character_found(self):
        """Displays toast popup when screenshot is captured but no 7DS character was recognized."""
        self.border_color = "#ef4444"  # Red alert
        self.lbl_header.setText("⚠️ NO 7DS CHARACTER DETECTED")
        self.lbl_header.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        self.lbl_name.setText("Screenshot captured, but no character spotted")
        self.lbl_badge.setVisible(False)
        self.lbl_attribute.setVisible(False)
        self.lbl_info.setText("Make sure character name/title/attribute is visible.")
        self.lbl_info.setStyleSheet("color: #94a3b8; font-size: 11px;")

        self._trigger_display()

    def _trigger_display(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + screen.width() - self.width() - 28
        y = screen.y() + screen.height() - self.height() - 28
        self.move(x, y)

        self.setWindowOpacity(0.0)
        self.show()
        self.apply_windows_topmost_noactivate(x, y)

        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(0.98)
        self.anim.start()

        self.update()

    def close_toast(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.hide)
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        rect = self.rect().adjusted(2, 2, -2, -2)
        path.addRoundedRect(rect, 10, 10)

        # Dark glass background
        painter.fillPath(path, QColor(15, 23, 42, 252))

        # Colored HUD border
        pen_color = QColor(self.border_color)
        painter.setPen(pen_color)
        painter.drawPath(path)
