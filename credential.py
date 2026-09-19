import sqlite3
import os
import bcrypt
from dotenv import load_dotenv



def test_credential(username, password):
    if not username or not password:
        return False
    password_bcode = password.encode("utf-8")
    load_dotenv()
    db = os.getenv("DATABASE")
    if not db:
        return False
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        cur.execute("SELECT username, password FROM users WHERE username = ?;", (username,))
        username_password = cur.fetchone()

    if not username_password:
        return False
    hash_db = username_password[1]
    if isinstance(hash_db, str):
        hash_db = hash_db.encode("utf-8")
    try:
        return bcrypt.checkpw(password_bcode, hash_db)
    except (ValueError, TypeError):
        return False
        
    
    