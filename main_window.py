# Main GUI Window for 7DS Grand Cross Snip Capture
import os
import sys
import csv
import json
import winsound
from datetime import datetime
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QColor, QFont, QKeySequence, QShortcut, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLineEdit, QComboBox, QMessageBox, QFileDialog, 
    QTextEdit, QFrame, QDialog, QFormLayout, QDialogButtonBox, 
    QCheckBox, QApplication, QAbstractItemView, QSystemTrayIcon, QMenu
)

from ocr_parser import SevenDSParser, ATTRIBUTE_MAP, RACES
from clipboard_monitor import ClipboardMonitor
from toast_overlay import ToastOverlay
import database

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0f172a;
}
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #1e293b;
    border-radius: 8px;
}
QTabBar::tab {
    background: #0f172a;
    color: #94a3b8;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    border: 1px solid #1e293b;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #1e293b;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}
QTabBar::tab:hover:!selected {
    background: #1e293b;
    color: #e2e8f0;
}
QPushButton {
    background-color: #334155;
    color: #ffffff;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #475569;
    border-color: #64748b;
}
QPushButton:pressed {
    background-color: #1e293b;
}
QPushButton#btn_start_monitor {
    background-color: #059669;
    color: #ffffff;
    border: 1px solid #10b981;
    font-size: 15px;
    padding: 12px 24px;
    border-radius: 8px;
}
QPushButton#btn_start_monitor:hover {
    background-color: #10b981;
}
QPushButton#btn_stop_monitor {
    background-color: #dc2626;
    color: #ffffff;
    border: 1px solid #ef4444;
    font-size: 15px;
    padding: 12px 24px;
    border-radius: 8px;
}
QPushButton#btn_stop_monitor:hover {
    background-color: #ef4444;
}
QLineEdit, QComboBox {
    background-color: #0f172a;
    color: #ffffff;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 12px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #ffffff;
    selection-background-color: #38bdf8;
    selection-color: #0f172a;
}
QTableWidget {
    background-color: #0f172a;
    gridline-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #f1f5f9;
}
QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #1e293b;
}
QTableWidget::item:selected {
    background-color: #1e293b;
    color: #38bdf8;
}
QHeaderView::section {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 8px;
    font-weight: bold;
    border: none;
    border-bottom: 2px solid #334155;
}
QTextEdit {
    background-color: #0b0f19;
    color: #cbd5e1;
    border: 1px solid #1e293b;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}
QCheckBox {
    color: #cbd5e1;
    font-weight: 500;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #0f172a;
}
QCheckBox::indicator:checked {
    background-color: #38bdf8;
    border-color: #38bdf8;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("7DS Grand Cross - Character & Attribute Snip-Capture")
        self.resize(1080, 700)
        self.setMinimumSize(900, 580)

        # Database & Core objects
        database.init_db()
        self.parser = SevenDSParser()
        self.toast = ToastOverlay()
        self.monitor = ClipboardMonitor(self.parser)

        # Connect monitor signals
        self.monitor.character_detected.connect(self.on_character_detected)
        self.monitor.no_character_detected.connect(self.on_no_character_detected)
        self.monitor.scan_status.connect(self.log_message)

        self.setStyleSheet(DARK_STYLESHEET)
        self.setup_ui()
        self.setup_tray()
        self.refresh_table()

    def setup_tray(self):
        """Setup system tray icon so app can run in background without taskbar clutter."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu(self)
        show_action = QAction("Open 7DS Capture", self)
        show_action.triggered.connect(self.showNormal)
        
        start_action = QAction("Toggle Start / Stop Monitor", self)
        start_action.triggered.connect(self.toggle_monitoring)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(start_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top Header Banner
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_vbox = QVBoxLayout()
        title_lbl = QLabel("⚔️ 7DS Grand Cross Snip Capture")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #f8fafc;")
        subtitle_lbl = QLabel("Auto-extract Character Names & Attributes on Win + Shift + S")
        subtitle_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_vbox.addWidget(title_lbl)
        title_vbox.addWidget(subtitle_lbl)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

        self.chk_sound = QCheckBox("🔊 Audio Alert")
        self.chk_sound.setChecked(True)
        self.chk_toast = QCheckBox("🪟 In-Game Toast Popup")
        self.chk_toast.setChecked(True)
        
        header_layout.addWidget(self.chk_sound)
        header_layout.addSpacing(12)
        header_layout.addWidget(self.chk_toast)

        main_layout.addWidget(header_widget)

        # Main Tabs
        self.tabs = QTabWidget()
        self.tab_monitor = QWidget()
        self.tab_list = QWidget()

        self.setup_monitor_tab()
        self.setup_list_tab()

        self.tabs.addTab(self.tab_monitor, "🎮 Snip Monitor & Controls")
        self.tabs.addTab(self.tab_list, "📜 7DS Character List")
        main_layout.addWidget(self.tabs)

    # ---------------- MONITOR TAB ----------------
    def setup_monitor_tab(self):
        layout = QVBoxLayout(self.tab_monitor)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Control Box
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background-color: #1e293b; border-radius: 10px; padding: 16px;")
        ctrl_layout = QVBoxLayout(ctrl_frame)

        self.btn_toggle_monitor = QPushButton("▶ START MONITORING (Ready to Capture)")
        self.btn_toggle_monitor.setObjectName("btn_start_monitor")
        self.btn_toggle_monitor.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_monitor.clicked.connect(self.toggle_monitoring)

        self.lbl_status = QLabel("Status: Monitor is currently STOPPED. Click Start to begin.")
        self.lbl_status.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ctrl_layout.addWidget(self.btn_toggle_monitor)
        ctrl_layout.addSpacing(6)
        ctrl_layout.addWidget(self.lbl_status)
        layout.addWidget(ctrl_frame)

        # How to Use Card
        guide_frame = QFrame()
        guide_frame.setStyleSheet("background-color: #1e293b; border-radius: 10px; padding: 14px; border-left: 4px solid #38bdf8;")
        guide_layout = QVBoxLayout(guide_frame)

        guide_title = QLabel("💡 Quick How-To Guide")
        guide_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 14px;")
        guide_text = QLabel(
            "1. Click <b>'Start Monitoring'</b> above.<br>"
            "2. Switch to <b>The Seven Deadly Sins: Grand Cross</b>.<br>"
            "3. Open any Character screen.<br>"
            "4. Press <b style='color:#e2e8f0; background:#334155; padding:2px 6px; border-radius:4px;'>Win + Shift + S</b> and snip the character.<br>"
            "5. The overlay popup will show what was saved! If no character was visible in the screenshot, it will notify you as well."
        )
        guide_text.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.5;")
        guide_layout.addWidget(guide_title)
        guide_layout.addWidget(guide_text)
        layout.addWidget(guide_frame)

        # Manual Test Section
        test_layout = QHBoxLayout()
        self.btn_test_file = QPushButton("📁 Test with Image File...")
        self.btn_test_file.clicked.connect(self.test_with_image_file)
        
        self.btn_view_list = QPushButton("👉 View Saved Characters List")
        self.btn_view_list.setStyleSheet("background-color: #2563eb; color: white;")
        self.btn_view_list.clicked.connect(lambda: self.tabs.setCurrentIndex(1))

        test_layout.addWidget(self.btn_test_file)
        test_layout.addStretch()
        test_layout.addWidget(self.btn_view_list)
        layout.addLayout(test_layout)

        # Activity Log
        log_label = QLabel("📋 Activity Log:")
        log_label.setStyleSheet("color: #94a3b8; font-weight: bold;")
        layout.addWidget(log_label)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(160)
        layout.addWidget(self.txt_log)

        self.log_message("System initialized. Ready.")

    # ---------------- CHARACTER LIST TAB ----------------
    def setup_list_tab(self):
        layout = QVBoxLayout(self.tab_list)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Filter & Search Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Search by character name or title...")
        self.txt_search.textChanged.connect(self.filter_table)

        self.cmb_attr_filter = QComboBox()
        self.cmb_attr_filter.addItem("All Attributes")
        for key, info in ATTRIBUTE_MAP.items():
            self.cmb_attr_filter.addItem(f"{info['name']} ({info['color_name']})", info['name'])
        self.cmb_attr_filter.currentIndexChanged.connect(self.filter_table)

        self.cmb_race_filter = QComboBox()
        self.cmb_race_filter.addItem("All Races")
        for r in RACES:
            self.cmb_race_filter.addItem(r, r)
        self.cmb_race_filter.currentIndexChanged.connect(self.filter_table)

        filter_bar.addWidget(self.txt_search, 2)
        filter_bar.addWidget(self.cmb_attr_filter, 1)
        filter_bar.addWidget(self.cmb_race_filter, 1)
        layout.addLayout(filter_bar)

        # Action Buttons Bar
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self.btn_copy_names_attrs = QPushButton("📋 Copy All (Name & Attribute)")
        self.btn_copy_names_attrs.setStyleSheet("background-color: #0284c7; color: white;")
        self.btn_copy_names_attrs.clicked.connect(self.copy_all_text)

        self.btn_copy_tsv = QPushButton("📊 Copy for Excel / Sheets")
        self.btn_copy_tsv.clicked.connect(self.copy_all_tsv)

        self.btn_export = QPushButton("💾 Export (CSV / TXT / JSON)")
        self.btn_export.clicked.connect(self.export_data)

        self.btn_add_manual = QPushButton("➕ Add Manually")
        self.btn_add_manual.clicked.connect(self.add_character_dialog)

        self.btn_delete_selected = QPushButton("🗑️ Delete Selected")
        self.btn_delete_selected.setStyleSheet("background-color: #b91c1c; color: white;")
        self.btn_delete_selected.clicked.connect(self.delete_selected_rows)

        self.btn_clear_all = QPushButton("🗑️ Clear All")
        self.btn_clear_all.setStyleSheet("background-color: #7f1d1d; color: #fca5a5;")
        self.btn_clear_all.clicked.connect(self.clear_all_dialog)

        action_bar.addWidget(self.btn_copy_names_attrs)
        action_bar.addWidget(self.btn_copy_tsv)
        action_bar.addWidget(self.btn_export)
        action_bar.addWidget(self.btn_add_manual)
        action_bar.addStretch()
        action_bar.addWidget(self.btn_delete_selected)
        action_bar.addWidget(self.btn_clear_all)
        layout.addLayout(action_bar)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Select", "ID", "Character Name & Title", "Attribute", "Race", "Combat Class", "Scans", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Bottom stats
        self.lbl_stats = QLabel("Total: 0 characters")
        self.lbl_stats.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.lbl_stats)

    # ---------------- MONITOR ACTIONS ----------------
    def toggle_monitoring(self):
        if not self.monitor.running:
            self.monitor.start()
            self.btn_toggle_monitor.setText("⏹ STOP MONITORING (Active - Listening for Win+Shift+S)")
            self.btn_toggle_monitor.setObjectName("btn_stop_monitor")
            self.btn_toggle_monitor.setStyleSheet("")
            self.lbl_status.setText("🟢 Status: ACTIVE. Switch to 7DS and press Win + Shift + S to capture characters!")
            self.lbl_status.setStyleSheet("color: #34d399; font-size: 13px; font-weight: bold;")
        else:
            self.monitor.stop()
            self.btn_toggle_monitor.setText("▶ START MONITORING (Ready to Capture)")
            self.btn_toggle_monitor.setObjectName("btn_start_monitor")
            self.btn_toggle_monitor.setStyleSheet("")
            self.lbl_status.setText("Status: Monitor is currently STOPPED.")
            self.lbl_status.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")

    def on_character_detected(self, char_data: dict, is_new: bool):
        self.refresh_table()

        if self.chk_sound.isChecked():
            try:
                winsound.MessageBeep(winsound.MB_OK)
            except Exception:
                pass

        if self.chk_toast.isChecked():
            self.toast.show_character(char_data, is_new)

    def on_no_character_detected(self):
        if self.chk_sound.isChecked():
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

        if self.chk_toast.isChecked():
            self.toast.show_no_character_found()

    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.append(f"[{timestamp}] {message}")

    def test_with_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select 7DS Screenshot", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.log_message(f"Testing with image: {os.path.basename(file_path)}")
            res, is_new = self.monitor.process_image_direct(file_path)
            if res:
                self.log_message(f"✅ Success! Captured: {res['full_name']} [{res['attribute_display']}]")

    # ---------------- TABLE DATA & FILTERING ----------------
    def refresh_table(self):
        self.all_characters = database.get_all_characters()
        self.filter_table()

    def filter_table(self):
        query = self.txt_search.text().lower().strip()
        selected_attr_data = self.cmb_attr_filter.currentData()
        selected_race = self.cmb_race_filter.currentText()

        filtered = []
        for char in self.all_characters:
            full_text = f"{char.get('full_name', '')} {char.get('title', '')} {char.get('name', '')}".lower()
            if query and query not in full_text:
                continue

            if selected_attr_data and char.get("attribute", "").upper() != selected_attr_data.upper():
                continue

            if selected_race != "All Races" and char.get("race", "").lower() != selected_race.lower():
                continue

            filtered.append(char)

        self.populate_table_rows(filtered)

    def populate_table_rows(self, char_list):
        self.table.setRowCount(len(char_list))
        self.current_filtered_list = char_list
        self.row_checkboxes = []

        for row, char in enumerate(char_list):
            # Checkbox for multi-select deletion
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(6, 0, 6, 0)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk = QCheckBox()
            chk.setProperty("char_id", char["id"])
            chk_layout.addWidget(chk)
            self.table.setCellWidget(row, 0, chk_widget)
            self.row_checkboxes.append(chk)

            # ID
            item_id = QTableWidgetItem(str(char["id"]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_id)

            # Name & Title
            full_name = char.get("full_name") or char.get("name", "")
            item_name = QTableWidgetItem(full_name)
            item_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 2, item_name)

            # Attribute badge text
            attr_display = char.get("attribute_display") or char.get("attribute", "Unknown")
            attr_key = char.get("attribute", "").upper()
            hex_color = ATTRIBUTE_MAP.get(attr_key, {}).get("hex", "#94a3b8")
            
            item_attr = QTableWidgetItem(attr_display)
            item_attr.setForeground(QColor(hex_color))
            item_attr.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.table.setItem(row, 3, item_attr)

            # Race
            race_val = char.get("race") or "-"
            item_race = QTableWidgetItem(race_val)
            item_race.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, item_race)

            # Combat Class
            cc_val = char.get("combat_class") or "-"
            item_cc = QTableWidgetItem(cc_val)
            item_cc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, item_cc)

            # Scans
            scans_val = f"{char.get('scan_count', 1)}x"
            item_scans = QTableWidgetItem(scans_val)
            item_scans.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, item_scans)

            # Actions Cell (Copy, Edit, Delete)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            btn_copy = QPushButton("📋")
            btn_copy.setToolTip("Copy character info")
            btn_copy.setFixedWidth(34)
            btn_copy.clicked.connect(lambda _, c=char: self.copy_single_character(c))

            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Edit character")
            btn_edit.setFixedWidth(34)
            btn_edit.clicked.connect(lambda _, c=char: self.edit_character_dialog(c))

            btn_delete = QPushButton("🗑️")
            btn_delete.setToolTip("Delete this character")
            btn_delete.setStyleSheet("background-color: #7f1d1d; color: white;")
            btn_delete.setFixedWidth(34)
            btn_delete.clicked.connect(lambda _, cid=char["id"]: self.delete_single_character(cid))

            action_layout.addWidget(btn_copy)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 7, action_widget)

        self.lbl_stats.setText(f"Showing {len(char_list)} of {len(self.all_characters)} characters")

    # ---------------- COPY & EXPORT ACTIONS ----------------
    def copy_single_character(self, char: dict):
        text = f"{char.get('full_name', '')} - {char.get('attribute_display', '')}"
        QApplication.clipboard().setText(text)
        self.log_message(f"📋 Copied to clipboard: {text}")

    def copy_all_text(self):
        lines = []
        for char in self.current_filtered_list:
            lines.append(f"{char.get('full_name', '')} - {char.get('attribute_display', '')}")
        
        full_text = "\n".join(lines)
        QApplication.clipboard().setText(full_text)
        QMessageBox.information(self, "Copied", f"Copied {len(lines)} character(s) to clipboard as text!")

    def copy_all_tsv(self):
        lines = ["Character Name\tTitle\tAttribute\tRace\tCombat Class\tScans"]
        for char in self.current_filtered_list:
            lines.append(
                f"{char.get('name', '')}\t{char.get('title', '')}\t{char.get('attribute_display', '')}\t{char.get('race', '')}\t{char.get('combat_class', '')}\t{char.get('scan_count', 1)}"
            )
        full_tsv = "\n".join(lines)
        QApplication.clipboard().setText(full_tsv)
        QMessageBox.information(self, "Copied for Sheets", f"Copied {len(lines)-1} character(s) to clipboard for Excel / Google Sheets!")

    def export_data(self):
        if not self.current_filtered_list:
            QMessageBox.warning(self, "Export", "No character records to export.")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Character Data", "7ds_characters.csv", 
            "CSV File (*.csv);;Text File (*.txt);;JSON File (*.json)"
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".csv") or "CSV" in selected_filter:
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Full Name", "Title", "Name", "Attribute", "Race", "Combat Class", "Scans", "Date Added"])
                    for c in self.current_filtered_list:
                        writer.writerow([
                            c["id"], c.get("full_name", ""), c.get("title", ""), c.get("name", ""),
                            c.get("attribute_display", ""), c.get("race", ""), c.get("combat_class", ""),
                            c.get("scan_count", 1), c.get("created_at", "")
                        ])
            elif file_path.endswith(".json") or "JSON" in selected_filter:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.current_filtered_list, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    for c in self.current_filtered_list:
                        f.write(f"{c.get('full_name', '')} | {c.get('attribute_display', '')} | Race: {c.get('race', '')}\n")

            QMessageBox.information(self, "Export Successful", f"Exported {len(self.current_filtered_list)} characters to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export file:\n{str(e)}")

    # ---------------- DIALOGS (MANUAL ADD / EDIT / DELETE) ----------------
    def add_character_dialog(self):
        dialog = CharacterEditDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            database.add_or_update_character(data)
            self.refresh_table()
            self.log_message(f"➕ Added manually: {data['full_name']} [{data['attribute_display']}]")

    def edit_character_dialog(self, char: dict):
        dialog = CharacterEditDialog(char_data=char, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            database.update_character(char["id"], data)
            self.refresh_table()
            self.log_message(f"✏️ Updated: {data['full_name']}")

    def delete_single_character(self, char_id: int):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this character entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_character(char_id)
            self.refresh_table()
            self.log_message(f"🗑️ Deleted character #{char_id}")

    def delete_selected_rows(self):
        """Deletes all checked rows in the table."""
        ids_to_delete = []
        for chk in getattr(self, "row_checkboxes", []):
            if chk.isChecked():
                ids_to_delete.append(chk.property("char_id"))

        if not ids_to_delete:
            # Check if any row is selected via highlight
            selected_rows = self.table.selectionModel().selectedRows()
            for index in selected_rows:
                row = index.row()
                if row < len(self.current_filtered_list):
                    ids_to_delete.append(self.current_filtered_list[row]["id"])

        if not ids_to_delete:
            QMessageBox.information(self, "Delete", "Please check or select at least one character to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete {len(ids_to_delete)} selected character(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for cid in ids_to_delete:
                database.delete_character(cid)
            self.refresh_table()
            self.log_message(f"🗑️ Deleted {len(ids_to_delete)} character(s).")

    def clear_all_dialog(self):
        reply = QMessageBox.warning(
            self, "Clear All Characters", 
            "Are you sure you want to delete ALL characters from the database? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.clear_all_characters()
            self.refresh_table()
            self.log_message("🗑️ Cleared all characters from database.")

    def closeEvent(self, event):
        if self.monitor.running:
            self.monitor.stop()
        event.accept()

class CharacterEditDialog(QDialog):
    def __init__(self, char_data: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Character Details" if char_data else "Add New Character")
        self.setFixedWidth(420)
        self.setStyleSheet(DARK_STYLESHEET)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("e.g. [The Seven Deadly Sins] or [Waves of the Earth]")
        
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Nemesis Meliodas or Queen Diane")

        self.cmb_attribute = QComboBox()
        for key, info in ATTRIBUTE_MAP.items():
            self.cmb_attribute.addItem(info["display"], key)

        self.cmb_race = QComboBox()
        for r in RACES:
            self.cmb_race.addItem(r)

        self.txt_cc = QLineEdit()
        self.txt_cc.setPlaceholderText("e.g. 71,168")

        form.addRow("Title / Prefix:", self.txt_title)
        form.addRow("Character Name:*", self.txt_name)
        form.addRow("Attribute:*", self.cmb_attribute)
        form.addRow("Race:", self.cmb_race)
        form.addRow("Combat Class:", self.txt_cc)
        layout.addLayout(form)

        if char_data:
            self.txt_title.setText(char_data.get("title", ""))
            self.txt_name.setText(char_data.get("name", ""))
            attr_key = char_data.get("attribute", "").upper()
            idx = self.cmb_attribute.findData(attr_key)
            if idx >= 0:
                self.cmb_attribute.setCurrentIndex(idx)
            
            race = char_data.get("race", "")
            r_idx = self.cmb_race.findText(race)
            if r_idx >= 0:
                self.cmb_race.setCurrentIndex(r_idx)
            
            self.txt_cc.setText(char_data.get("combat_class", ""))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Validation", "Character Name cannot be empty.")
            return
        self.accept()

    def get_data(self) -> dict:
        title = self.txt_title.text().strip()
        name = self.txt_name.text().strip()
        full_name = f"{title} {name}".strip() if title else name
        attr_key = self.cmb_attribute.currentData()
        attr_info = ATTRIBUTE_MAP.get(attr_key, {})

        return {
            "title": title,
            "name": name,
            "full_name": full_name,
            "attribute": attr_info.get("name", attr_key),
            "attribute_color": attr_info.get("color_name", ""),
            "attribute_display": attr_info.get("display", attr_key),
            "attribute_hex": attr_info.get("hex", "#94a3b8"),
            "race": self.cmb_race.currentText(),
            "combat_class": self.txt_cc.text().strip()
        }
