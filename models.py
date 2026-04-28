from db import get_connection


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    # ==========================
    # STUDENTS TABLE
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT NOT NULL,
        roll TEXT,
        mobile TEXT,
        email TEXT,
        department TEXT,
        semester TEXT,
        address TEXT
    )
    """)

    # ==========================
    # USERS TABLE (Login/Register)
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT NOT NULL
    )
    """)

    # ==========================
    # ATTENDANCE TABLE
    # ==========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        student_name TEXT,
        date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()