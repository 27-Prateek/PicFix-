# src/database.py
import sqlite3
import hashlib
import os

DATABASE_FILE = "photo_editor.db"

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize the SQLite database with users and images tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # Users table: stores username, hashed password, security question, hashed answer
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            security_question TEXT NOT NULL,
            security_answer TEXT NOT NULL
        )
    """)
    # Images table: stores image path and username of editor
    c.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            username TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password, security_question, security_answer):
    """Add a new user to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), security_question, hash_password(security_answer)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def get_security_question(username):
    """Get the security question and hashed answer for a user."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT security_question, security_answer FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result  # Returns (question, hashed_answer) or None

def reset_password(username, new_password, security_answer):
    """Reset a user's password if the security answer matches."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT security_answer FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    if result and result[0] == hash_password(security_answer):
        c.execute("UPDATE users SET password = ? WHERE username = ?",
                  (hash_password(new_password), username))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def delete_all_users():
    """Delete all users and their image history."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM images")
    conn.commit()
    conn.close()

def add_image_edit(image_path, username):
    """Record an image edit by a user."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO images (image_path, username) VALUES (?, ?)", (image_path, username))
    conn.commit()
    conn.close()

def get_user_images(username):
    """Get all images edited by a user."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT image_path FROM images WHERE username = ?", (username,))
    results = c.fetchall()
    conn.close()
    return [row[0] for row in results]