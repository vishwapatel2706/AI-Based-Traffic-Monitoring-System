import sqlite3
import json
from datetime import datetime

class ViolationsDatabase:
    def __init__(self, db_path='violations.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    vehicle_type TEXT,
                    details TEXT,  -- JSON string
                    image_path TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def add_violation(self, violation_type, vehicle_type, details, image_path=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO violations (type, vehicle_type, details, image_path)
                VALUES (?, ?, ?, ?)
            ''', (violation_type, vehicle_type, json.dumps(details), image_path))

    def get_violations(self, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM violations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

    def get_violations_by_type(self, violation_type, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM violations
                WHERE type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (violation_type, limit))
            return cursor.fetchall()