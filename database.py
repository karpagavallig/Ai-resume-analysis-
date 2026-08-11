import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "database.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_db():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# REGISTER USER
# ==========================================

def register_user(username, email, password):

    connection = get_connection()

    try:

        hashed_password = generate_password_hash(password)

        connection.execute("""
            INSERT INTO users
            (username, email, password)
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            hashed_password
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


# ==========================================
# LOGIN USER
# ==========================================

def login_user(email, password):

    connection = get_connection()

    user = connection.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,)).fetchone()

    connection.close()

    if user:

        if check_password_hash(
            user["password"],
            password
        ):
            return user

    return None