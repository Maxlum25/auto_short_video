import sqlite3
import os
import getpass
from dotenv import load_dotenv
import bcrypt



def main():
    load_dotenv()
    DATABASE = os.getenv("DATABASE")
    if not DATABASE:
        print("Falta DATABASE en el entorno (.env)")
        return
    while True:
        username = input("Ingresa el usuario: ").strip()
        if not username:
            print("El usuario no puede estar vacío.")
            continue
        password = getpass.getpass(f"Ingresa la contraseña de {username}: ")
        if not password:
            print("La contraseña no puede estar vacía.")
            continue
        confirm = input(f"¿Crear el usuario '{username}'? 's/n': ")
        if confirm.lower() == "s":
            break

    password_bcode = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bcode, bcrypt.gensalt())

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password BLOB NOT NULL )
        """)

        cur.execute("""
            INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
        """, (username, hashed))

        con.commit()

    # Opcional: Verificar si se insertó realmente
    if cur.rowcount == 0:
        print("El usuario ya existía, no se hizo nada.")
    else:
        print("Usuario creado exitosamente.")
        
    
    
    
    
if __name__ == "__main__":
    
    main()

