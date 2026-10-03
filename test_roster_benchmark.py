# Comprehensive 7DS Grand Cross Character Roster Benchmark
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from ocr_parser import SevenDSParser

TEST_ROSTER = [
    # 1. Festival & LR Darkness Units
    {
        "title": "[The Seven Deadly Sins]",
        "name": "Nemesis Meliodas",
        "attribute": "Darkness",
        "race": "Demon",
        "cc": "73,143"
    },
    {
        "title": "[The Ruler]",
        "name": "Demon King Meliodas",
        "attribute": "Darkness",
        "race": "Demon",
        "cc": "74,200"
    },
    {
        "title": "[Twisted Fate]",
        "name": "Purgatory Meliodas",
        "attribute": "Darkness",
        "race": "Demon",
        "cc": "70,890"
    },
    # 2. Light Units
    {
        "title": "[Transcendence of Life]",
        "name": "Ultimate Escanor",
        "attribute": "Light",
        "race": "Human",
        "cc": "72,500"
    },
    {
        "title": "[Brilliant Protection]",
        "name": "Queen Elizabeth",
        "attribute": "Light",
        "race": "Goddess",
        "cc": "71,430"
    },
    {
        "title": "[Sun of God]",
        "name": "Sunshine Mael",
        "attribute": "Light",
        "race": "Goddess",
        "cc": "69,920"
    },
    # 3. Strength / Red Units (including unbracketed title format)
    {
        "title": "[Waves of the Earth]",
        "name": "Queen Diane",
        "attribute": "Strength",
        "race": "Giant",
        "cc": "71,168"
    },
    {
        "title": "Knight of Wrath",
        "name": "Demon Meliodas",
        "attribute": "Strength",
        "race": "Demon",
        "cc": "64,300"
    },
    {
        "title": "[Holy War]",
        "name": "Estarossa of Love",
        "attribute": "Strength",
        "race": "Demon",
        "cc": "66,800"
    },
    # 4. Speed / Blue Units
    {
        "title": "[Vengeful Saw Blade]",
        "name": "Roxy of Madness",
        "attribute": "Speed",
        "race": "Human",
        "cc": "66,947"
    },
    {
        "title": "[Covenant of Light]",
        "name": "Ludociel of Flash",
        "attribute": "Speed",
        "race": "Goddess",
        "cc": "68,200"
    },
    {
        "title": "[The Four Archangels]",
        "name": "Ryudoshel of Grace",
        "attribute": "Speed",
        "race": "Goddess",
        "cc": "65,400"
    },
    # 5. HP / Green Units
    {
        "title": "[Curse of Immortality]",
        "name": "Purgatory Ban",
        "attribute": "HP",
        "race": "Human",
        "cc": "70,100"
    },
    {
        "title": "[Fairy King's Forest]",
        "name": "King the Harlequin",
        "attribute": "HP",
        "race": "Fairy",
        "cc": "67,500"
    },
    {
        "title": "Forest Guardian",
        "name": "Helbram",
        "attribute": "HP",
        "race": "Fairy",
        "cc": "61,200"
    },
    # 6. Collab Characters
    {
        "title": "[Re:ZERO]",
        "name": "Subaru & Beatrice",
        "attribute": "Darkness",
        "race": "Human",
        "cc": "69,584"
    },
    {
        "title": "[Re:ZERO]",
        "name": "Ruler Candidate Rem",
        "attribute": "Speed",
        "race": "Demon",
        "cc": "65,800"
    },
    {
        "title": "[Re:ZERO]",
        "name": "Twin Maid Ram",
        "attribute": "HP",
        "race": "Unknown",
        "cc": "63,400"
    },
    {
        "title": "[Overlord]",
        "name": "Ainz Ooal Gown",
        "attribute": "Darkness",
        "race": "Unknown",
        "cc": "72,100"
    },
    {
        "title": "[Overlord]",
        "name": "Albedo of Pure White",
        "attribute": "Strength",
        "race": "Unknown",
        "cc": "70,400"
    },
    {
        "title": "[Mushoku Tensei]",
        "name": "Rudeus Greyrat",
        "attribute": "HP",
        "race": "Unknown",
        "cc": "68,900"
    },
    {
        "title": "[Slime]",
        "name": "Demon Lord Rimuru Tempest",
        "attribute": "Speed",
        "race": "Unknown",
        "cc": "71,000"
    },
    {
        "title": "[Attack on Titan]",
        "name": "Eren Jaeger",
        "attribute": "Strength",
        "race": "Human",
        "cc": "64,700"
    },
    {
        "title": "[KOF '98]",
        "name": "Rugal Bernstein",
        "attribute": "HP",
        "race": "Human",
        "cc": "62,500"
    }
]

def get_font(size):
    # Try Windows system fonts
    font_paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def generate_7ds_screenshot(char_info) -> Image.Image:
    img = Image.new('RGB', (1100, 700), color='#e8d3b5')
    draw = ImageDraw.Draw(img)

    f_title = get_font(20)
    f_name = get_font(24)
    f_stat_lbl = get_font(16)
    f_stat_val = get_font(16)

    # Top rarity badge
    draw.text((430, 45), "[LR]", fill="#9333ea", font=f_title)
    
    # Title (upper line) and Name (lower line)
    title_text = char_info["title"]
    name_text = char_info["name"]
    draw.text((510, 45), title_text, fill="#382c1e", font=f_title)
    draw.text((510, 75), name_text, fill="#1c1917", font=f_name)

    # Left Stats Panel
    draw.text((30, 135), "Lv.100/100", fill="#44403c", font=f_stat_lbl)
    draw.text((30, 165), "Awaken", fill="#57534e", font=f_stat_lbl)
    
    # Attribute
    draw.text((30, 195), "Attribute", fill="#57534e", font=f_stat_lbl)
    draw.text((125, 195), char_info["attribute"], fill="#1c1917", font=f_stat_val)
    
    # Race
    draw.text((30, 225), "Race", fill="#57534e", font=f_stat_lbl)
    draw.text((125, 225), char_info["race"], fill="#1c1917", font=f_stat_val)

    # Characteristics & Combat Class
    draw.text((30, 255), "Characteristics", fill="#57534e", font=f_stat_lbl)
    draw.text((30, 285), "Combat Class", fill="#57534e", font=f_stat_lbl)
    draw.text((135, 285), char_info["cc"], fill="#1c1917", font=f_stat_val)
    
    draw.text((30, 315), "Attack", fill="#57534e", font=f_stat_lbl)
    draw.text((135, 315), "15,200", fill="#1c1917", font=f_stat_val)
    draw.text((30, 345), "Defense", fill="#57534e", font=f_stat_lbl)
    draw.text((135, 345), "12,100", fill="#1c1917", font=f_stat_val)
    draw.text((30, 375), "HP", fill="#57534e", font=f_stat_lbl)
    draw.text((135, 375), "205,000", fill="#1c1917", font=f_stat_val)

    return img

def run_benchmark():
    parser = SevenDSParser()
    passed = 0
    total = len(TEST_ROSTER)

    print(f"=== Starting 7DS Roster Benchmark ({total} Characters) ===\n")

    for i, char_info in enumerate(TEST_ROSTER, 1):
        img = generate_7ds_screenshot(char_info)
        res = parser.parse_image(img)
        
        if not res:
            print(f"[{i:02d}/{total}] [FAIL]: OCR returned None for {char_info['name']}")
            continue

        # Match name ignoring minor spaces
        clean_exp = char_info["name"].replace(" ", "").lower()
        clean_got = res["full_name"].replace(" ", "").lower()
        name_match = (clean_exp in clean_got)
        attr_match = (char_info["attribute"].lower() == res["attribute"].lower())

        if name_match and attr_match:
            passed += 1
            print(f"[{i:02d}/{total}] [PASS] {res['full_name']:<48} | {res['attribute_display']:<18} | Race: {res['race']}")
        else:
            print(f"[{i:02d}/{total}] [FAIL] Expected {char_info['name']} ({char_info['attribute']}), got {res['full_name']} ({res['attribute']})")

    print(f"\n==================================================")
    print(f"Benchmark Results: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print(f"==================================================")

if __name__ == "__main__":
    run_benchmark()
