import sqlite3
import os
import json
import secrets
from datetime import datetime

class UsersDatabase:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def create_user(self, email, password_hash):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO users (email, password_hash)
                    VALUES (?, ?)
                ''', (email, password_hash))
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        except Exception as e:
            return False, str(e)

    def get_user_by_email(self, email):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT id, email, password_hash FROM users WHERE email = ?', (email,))
            return cursor.fetchone()

    def update_user_token(self, user_id):
        token = secrets.token_hex(32)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE users SET token = ? WHERE id = ?', (token, user_id))
        return token

    def verify_token(self, token):
        if not token:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT id, email FROM users WHERE token = ?', (token,))
            return cursor.fetchone()

    def logout_user(self, token):
        if token:
           with sqlite3.connect(self.db_path) as conn:
               conn.execute('UPDATE users SET token = NULL WHERE token = ?', (token,))
