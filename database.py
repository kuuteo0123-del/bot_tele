"""ุ
💾 DATABASE - Lưu & track submissions
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from logger_setup import logger
from config import Config

class Database:
    """Database manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS submissions
            (id INTEGER PRIMARY KEY,
             code TEXT,
             username TEXT,
             url TEXT,
             status TEXT,
             result TEXT,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    def record_submission(self, code: str, username: str, url: str, status: str, result: str = ""):
        """Record submission"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO submissions (code, username, url, status, result)
                     VALUES (?, ?, ?, ?, ?)''',
                  (code, username, url, status, result))
        
        conn.commit()
        conn.close()
    
    def get_submission_history(self, limit: int = 100) -> list:
        """Get submission history"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM submissions ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> dict:
        """Get statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) as total FROM submissions')
        total = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) as success FROM submissions WHERE status = "SUCCESS"')
        success = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) as failed FROM submissions WHERE status = "FAILED"')
        failed = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'success_rate': (success / total * 100) if total > 0 else 0
        }

# Global instance
_database = None

def init_database(db_path: str) -> Database:
    global _database
    if _database is None:
        _database = Database(db_path)
    return _database

def get_database() -> Database:
    global _database
    if _database is None:
        init_database(Config.DATABASE_PATH)
    return _database
