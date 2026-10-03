import sqlite3
import os
import json
from datetime import datetime

class ModelsDatabase:
    def __init__(self, db_path='models.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    encoder_path TEXT,
                    type TEXT NOT NULL,  -- 'classification' or 'detection'
                    classes TEXT,  -- JSON string of classes
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 0
                )
            ''')

    def add_model(self, name, model_path, encoder_path=None, model_type='classification', classes=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO models (name, path, encoder_path, type, classes)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, model_path, encoder_path, model_type, json.dumps(classes) if classes else None))

    def get_models(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM models ORDER BY created_at DESC')
            return cursor.fetchall()

    def set_active_model(self, model_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE models SET active = 0')
            conn.execute('UPDATE models SET active = 1 WHERE id = ?', (model_id,))

    def get_active_model(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM models WHERE active = 1 LIMIT 1')
            return cursor.fetchone()

    def delete_model(self, model_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM models WHERE id = ?', (model_id,))