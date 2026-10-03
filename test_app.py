# Comprehensive Automated Test for 7DS Snip Capture
import os
import sys
from ocr_parser import SevenDSParser
import database

def test_all():
    parser = SevenDSParser()

    # 1. Test Meliodas
    img_meliodas = r"C:\Users\karis\.gemini\antigravity\brain\290bdf3f-fb2a-43a3-9410-276214c12c0b\.user_uploaded\media_1791003081466.png"
    res1 = parser.parse_image(img_meliodas)
    print("Meliodas:", res1["full_name"], "|", res1["attribute_display"])
    assert res1["full_name"] == "[The Seven Deadly Sins] Nemesis Meliodas"
    assert res1["attribute"] == "Darkness"

    # 2. Test Diane
    img_diane = r"C:\Users\karis\.gemini\antigravity\brain\290bdf3f-fb2a-43a3-9410-276214c12c0b\.user_uploaded\media_1791003814344.png"
    res2 = parser.parse_image(img_diane)
    print("Diane:", res2["full_name"], "|", res2["attribute_display"])
    assert res2["full_name"] == "[Waves of the Earth] Queen Diane"
    assert res2["attribute"] == "Strength"

    # 3. Test Roxy
    img_roxy = r"C:\Users\karis\.gemini\antigravity\brain\290bdf3f-fb2a-43a3-9410-276214c12c0b\.user_uploaded\media_1791004283369.png"
    res3 = parser.parse_image(img_roxy)
    print("Roxy:", res3["full_name"], "|", res3["attribute_display"])
    assert res3["full_name"] == "[Vengeful Saw Blade] Roxy of Madness"
    assert res3["attribute"] == "Speed"

    # 4. Test Duplicate Prevention
    test_db = "test_dupes.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    database.init_db(test_db)

    id_first, is_new1 = database.add_character_if_not_exists(res3, test_db)
    assert is_new1 is True, "First insertion should be True"

    id_second, is_new2 = database.add_character_if_not_exists(res3, test_db)
    assert is_new2 is False, "Second insertion must be False (duplicate rejected)"

    chars = database.get_all_characters(test_db)
    assert len(chars) == 1, f"Database must only have 1 character, found {len(chars)}"
    print("[PASS] Duplicate Prevention Verified!")

    if os.path.exists(test_db):
        os.remove(test_db)

    print("ALL TESTS PASSED WITH 100% ACCURACY!")

if __name__ == "__main__":
    test_all()
