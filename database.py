# SQLite Database for 7DS Characters
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

DB_NAME = "characters.db"

def get_db_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)

def init_db(db_path: Optional[str] = None):
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            attribute TEXT NOT NULL,
            attribute_color TEXT,
            attribute_display TEXT,
            race TEXT,
            combat_class TEXT,
            scan_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_text TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_character_if_not_exists(data: Dict[str, Any], db_path: Optional[str] = None) -> Tuple[int, bool]:
    """
    Inserts character ONLY if it does not already exist with the same name & attribute.
    Returns (char_id, is_new).
    If it already exists, returns (existing_id, False) without adding a duplicate.
    """
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    full_name = data.get("full_name", "").strip()
    attribute = data.get("attribute", "").strip()
    name = data.get("name", "").strip()
    title = data.get("title", "").strip()
    attribute_color = data.get("attribute_color", "")
    attribute_display = data.get("attribute_display", "")
    race = data.get("race", "")
    combat_class = data.get("combat_class", "")
    raw_text = data.get("raw_text", "")

    # Check for duplicate
    cur.execute("""
        SELECT id FROM characters 
        WHERE (LOWER(full_name) = LOWER(?) OR (LOWER(name) = LOWER(?) AND LOWER(title) = LOWER(?))) 
          AND LOWER(attribute) = LOWER(?)
    """, (full_name, name, title, attribute))
    row = cur.fetchone()

    if row:
        char_id = row[0]
        conn.close()
        return char_id, False  # Already exists!
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO characters (
                title, name, full_name, attribute, attribute_color, 
                attribute_display, race, combat_class, scan_count, 
                created_at, updated_at, raw_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
        """, (
            title, name, full_name, attribute, attribute_color,
            attribute_display, race, combat_class, now, now, raw_text
        ))
        char_id = cur.lastrowid
        conn.commit()
        conn.close()
        return char_id, True  # Newly added!

# Alias for backward compatibility
add_or_update_character = add_character_if_not_exists

def get_all_characters(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters ORDER BY id DESC")
    rows = cur.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def update_character(char_id: int, data: Dict[str, Any], db_path: Optional[str] = None):
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        UPDATE characters 
        SET title = ?, name = ?, full_name = ?, attribute = ?, 
            attribute_display = ?, race = ?, combat_class = ?, updated_at = ?
        WHERE id = ?
    """, (
        data.get("title", ""),
        data.get("name", ""),
        data.get("full_name", ""),
        data.get("attribute", ""),
        data.get("attribute_display", ""),
        data.get("race", ""),
        data.get("combat_class", ""),
        now,
        char_id
    ))
    conn.commit()
    conn.close()

def delete_character(char_id: int, db_path: Optional[str] = None):
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("DELETE FROM characters WHERE id = ?", (char_id,))
    conn.commit()
    conn.close()

def clear_all_characters(db_path: Optional[str] = None):
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("DELETE FROM characters")
    conn.commit()
    conn.close()
