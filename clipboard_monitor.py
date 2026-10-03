# Clipboard Monitor Thread for 7DS Snip Capture
import time
import hashlib
from io import BytesIO
from typing import Optional
from PIL import Image, ImageGrab
from PySide6.QtCore import QThread, Signal
from ocr_parser import SevenDSParser
import database

class ClipboardMonitor(QThread):
    character_detected = Signal(dict, bool)  # (character_data, is_new)
    no_character_detected = Signal()          # emitted when screenshot had no 7DS data
    scan_status = Signal(str)                # status message for logs

    def __init__(self, parser: Optional[SevenDSParser] = None, parent=None):
        super().__init__(parent)
        self.parser = parser or SevenDSParser()
        self.running = False
        self.last_image_hash: Optional[str] = None

    def run(self):
        self.running = True
        self.scan_status.emit("🟢 Clipboard monitor active. Ready for Win + Shift + S snips.")
        
        while self.running:
            try:
                img = ImageGrab.grabclipboard()
                if isinstance(img, Image.Image):
                    # Compute quick hash of image bytes
                    img_byte_arr = BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    img_hash = hashlib.md5(img_bytes).hexdigest()

                    if img_hash != self.last_image_hash:
                        self.last_image_hash = img_hash
                        self.scan_status.emit("📸 New screenshot detected in clipboard. Analyzing...")
                        
                        char_data = self.parser.parse_image(img)
                        if char_data and (char_data.get("name") or char_data.get("attribute") != "Unknown"):
                            char_id, is_new = database.add_character_if_not_exists(char_data)
                            if is_new:
                                self.scan_status.emit(f"✅ Added: {char_data['full_name']} [{char_data['attribute_display']}]")
                            else:
                                self.scan_status.emit(f"⚠️ Duplicate skipped (already in list): {char_data['full_name']}")
                            self.character_detected.emit(char_data, is_new)
                        else:
                            self.scan_status.emit("⚠️ Screenshot captured, but no 7DS character profile detected.")
                            self.no_character_detected.emit()
            except Exception as e:
                pass

            time.sleep(0.35)

    def stop(self):
        self.running = False
        self.wait(1000)
        self.scan_status.emit("⏹️ Clipboard monitor stopped.")

    def process_image_direct(self, img_input):
        """Processes a file or PIL image directly."""
        char_data = self.parser.parse_image(img_input)
        if char_data:
            char_id, is_new = database.add_character_if_not_exists(char_data)
            self.character_detected.emit(char_data, is_new)
            return char_data, is_new
        else:
            self.no_character_detected.emit()
            return None, False
