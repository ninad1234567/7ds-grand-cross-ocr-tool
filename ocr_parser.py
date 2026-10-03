# 7DS Grand Cross OCR and Entity Parser
import re
from typing import Dict, Any, Optional, List, Tuple
from rapidocr_onnxruntime import RapidOCR

ATTRIBUTE_MAP = {
    "DARKNESS": {"name": "Darkness", "color_name": "Purple / Dark", "hex": "#a855f7", "display": "Darkness (Purple)"},
    "LIGHT": {"name": "Light", "color_name": "Yellow / Light", "hex": "#eab308", "display": "Light (Yellow)"},
    "STRENGTH": {"name": "Strength", "color_name": "Red", "hex": "#ef4444", "display": "Strength (Red)"},
    "HP": {"name": "HP", "color_name": "Green", "hex": "#22c55e", "display": "HP (Green)"},
    "SPEED": {"name": "Speed", "color_name": "Blue", "hex": "#3b82f6", "display": "Speed (Blue)"},
}

RACES = ["Demon", "Goddess", "Human", "Fairy", "Giant", "Unknown"]

def fix_text_spacing(s: str) -> str:
    """Fixes OCR spacing quirks and camelCase words."""
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
    # Collapse double spaces
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def is_stat_line(text: str) -> bool:
    """Accurately filters out stat labels and rarity badges ([LR], [UR], etc.)."""
    upper = text.upper().strip()
    
    clean = re.sub(r"[\[\]\(\)\s]", "", upper)
    rarities = {"R", "SR", "SSR", "UR", "LR", "MAX", "CP", "HP", "CC", "ATK", "DEF"}
    if clean in rarities or upper in rarities:
        return True

    exact_keywords = {
        "AWAKEN", "ATTRIBUTE", "RACE", "CHARACTERISTICS", "SKILLS", "UNIQUE",
        "COMBAT", "CLASS", "COMBAT CLASS", "ATTACK", "DEFENSE", "AFFINITY",
        "UNITY/UNIQUE", "UNITY"
    }
    if upper in exact_keywords or clean in exact_keywords:
        return True

    prefix_keywords = ["LV.", "LV ", "LEVEL", "AFFINITY LV", "AFFINITYLV", "AFFINITY:"]
    if any(upper.startswith(p) for p in prefix_keywords):
        return True

    if re.match(r"^[\d,\./\s\:\+\%]+$", text):
        return True

    return False

class SevenDSParser:
    def __init__(self):
        self.ocr = RapidOCR()

    def parse_image(self, image_input) -> Optional[Dict[str, Any]]:
        import numpy as np
        from PIL import Image

        if isinstance(image_input, Image.Image):
            image_np = np.array(image_input.convert("RGB"))
        else:
            image_np = image_input

        ocr_results, _ = self.ocr(image_np)
        if not ocr_results:
            return None

        lines_data: List[Tuple[str, float, float, float]] = []
        for item in ocr_results:
            box = item[0]
            text = item[1].strip()
            conf = float(item[2])
            ys = [p[1] for p in box]
            xs = [p[0] for p in box]
            lines_data.append((text, sum(ys) / len(ys), sum(xs) / len(xs), conf))

        return self.extract_character_info(lines_data)

    def extract_character_info(self, lines_data: List[Tuple[str, float, float, float]]) -> Optional[Dict[str, Any]]:
        if not lines_data:
            return None

        lines_data.sort(key=lambda x: x[1])
        all_texts = [item[0] for item in lines_data]
        joined_text = " \n ".join(all_texts)

        # 1. Attribute Extraction (Precise targeting to avoid confusing HP stat with HP attribute)
        attr_info = None

        # Priority 1: Match directly on or immediately adjacent to the "Attribute" line
        for i, (text, y, x, conf) in enumerate(lines_data):
            upper = text.upper()
            if "ATTRIBUTE" in upper:
                for k, v in ATTRIBUTE_MAP.items():
                    if k in upper:
                        attr_info = v
                        break
                if not attr_info and i + 1 < len(lines_data):
                    next_upper = lines_data[i+1][0].upper().strip()
                    for k, v in ATTRIBUTE_MAP.items():
                        if k == next_upper or re.search(rf"\b{k}\b", next_upper):
                            attr_info = v
                            break
            if attr_info:
                break

        # Priority 2: In the attribute section (y in [160, 230], x in [70, 220])
        if not attr_info:
            for text, y, x, conf in lines_data:
                if 160 <= y <= 240:
                    upper = text.upper().strip()
                    for k, v in ATTRIBUTE_MAP.items():
                        if k == "HP":
                            if upper == "HP" and y < 220:
                                attr_info = v
                                break
                        elif k in upper:
                            attr_info = v
                            break
                if attr_info:
                    break

        # Priority 3: Fallback anywhere (excluding pure HP stat line)
        if not attr_info:
            for text, y, x, conf in lines_data:
                upper = text.upper().strip()
                for k, v in ATTRIBUTE_MAP.items():
                    if k != "HP" and re.search(rf"\b{k}\b", upper):
                        attr_info = v
                        break
                if attr_info:
                    break

        # 2. Race
        race = "Unknown"
        for text, y, x, conf in lines_data:
            for r in RACES:
                if r.upper() in text.upper():
                    race = r
                    break
            if race != "Unknown":
                break

        # 3. Combat Class
        combat_class = ""
        cc_pattern = re.compile(r"(\d{1,3},\d{3})")
        for text, y, x, conf in lines_data:
            if y > 140 and x < 250:
                m = cc_pattern.search(text)
                if m:
                    combat_class = m.group(1)
                    break

        # 4. Extract Header Lines (Title & Name)
        header_candidates = []
        for text, y, x, conf in lines_data:
            if y < 35: # top currency or account bar
                continue
            if is_stat_line(text):
                continue
            if x < 150 and y > 120: # left stat panel
                continue
            if len(text) >= 2:
                header_candidates.append((text, y, x))

        title = ""
        name = ""

        if len(header_candidates) >= 2:
            c1, c2 = header_candidates[0], header_candidates[1]
            if abs(c2[1] - c1[1]) < 70:
                t_raw = c1[0].strip()
                n_raw = fix_text_spacing(c2[0].strip())
                
                if not t_raw.startswith("["):
                    title = f"[{t_raw}]"
                else:
                    title = t_raw
                name = n_raw
            else:
                raw = c1[0].strip()
                m = re.match(r"(\[[^\]]+\])\s*(.*)", raw)
                if m:
                    title = m.group(1).strip()
                    name = fix_text_spacing(m.group(2).strip()) if m.group(2).strip() else fix_text_spacing(c2[0])
                else:
                    name = fix_text_spacing(raw)
        elif len(header_candidates) == 1:
            raw = header_candidates[0][0].strip()
            m = re.match(r"(\[[^\]]+\])\s*(.*)", raw)
            if m:
                title = m.group(1).strip()
                name = fix_text_spacing(m.group(2).strip()) if m.group(2).strip() else title
            else:
                name = fix_text_spacing(raw)

        if not name and not attr_info:
            return None

        # Clean formatting
        if title and name and title == name:
            full_display_name = title
        elif title and name:
            full_display_name = f"{title} {name}".strip()
        else:
            full_display_name = name or title

        attr_display = attr_info["display"] if attr_info else "Unknown"
        attr_name = attr_info["name"] if attr_info else "Unknown"
        attr_color = attr_info["color_name"] if attr_info else "Unknown"
        attr_hex = attr_info["hex"] if attr_info else "#94a3b8"

        return {
            "title": title,
            "name": name if name else full_display_name,
            "full_name": full_display_name,
            "attribute": attr_name,
            "attribute_color": attr_color,
            "attribute_display": attr_display,
            "attribute_hex": attr_hex,
            "race": race,
            "combat_class": combat_class,
            "raw_text": joined_text
        }
