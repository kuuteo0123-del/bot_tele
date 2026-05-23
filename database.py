"""
📊 DATABASE MANAGEMENT (v3.6 - FIXED & THREAD-SAFE)
Lưu trữ history, tracking codes, analytics với proper lock handling
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from logger_setup import logger


class CodeDatabase:
    """Quản lý database SQLite (thread-safe)"""
    
    def __init__(self, db_path: str = "data/code_history.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # ✅ Dùng threading.Lock thay vì asyncio.Lock vì đây là hàm đồng bộ
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """Tạo các bảng và chỉ mục cần thiết"""
        try:
            with self._lock:
                # Bảng code_submission
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS code_submission (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        account TEXT NOT NULL,
                        website TEXT NOT NULL,
                        status TEXT,
                        result TEXT,
                        submitted_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Bảng submission_log
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS submission_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL,
                        account TEXT NOT NULL,
                        website TEXT NOT NULL,
                        status TEXT,
                        result TEXT,
                        attempt INTEGER,
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Bảng account_stats
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS account_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account TEXT NOT NULL UNIQUE,
                        total_submitted INTEGER DEFAULT 0,
                        total_success INTEGER DEFAULT 0,
                        total_failed INTEGER DEFAULT 0,
                        last_submit TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Bảng website_stats
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS website_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        website TEXT NOT NULL UNIQUE,
                        total_submitted INTEGER DEFAULT 0,
                        total_success INTEGER DEFAULT 0,
                        total_failed INTEGER DEFAULT 0,
                        last_submit TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tạo chỉ mục để tăng tốc truy vấn
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_code ON code_submission(code)")
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_account ON submission_log(account)")
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_website ON submission_log(website)")
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_submitted_at ON submission_log(submitted_at)")
                
                self.conn.commit()
            logger.info("✅ Database tables khởi tạo xong")
        except Exception as e:
            logger.error(f"❌ Lỗi tạo tables: {e}")
            raise
    
    def record_submission(self, 
                         code: str, 
                         account: str, 
                         website: str, 
                         status: str, 
                         result: str = None,
                         attempt: int = 1):
        """Ghi lại submission (thread-safe)"""
        with self._lock:
            try:
                # Chèn vào submission_log
                self.conn.execute("""
                    INSERT INTO submission_log 
                    (code, account, website, status, result, attempt)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, account, website, status, result, attempt))
                
                # Cập nhật hoặc chèn vào code_submission
                self.conn.execute("""
                    INSERT OR REPLACE INTO code_submission 
                    (code, account, website, status, result, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, account, website, status, result, datetime.now()))
                
                # Cập nhật account_stats
                self.conn.execute("""
                    INSERT INTO account_stats (account, total_submitted, last_submit)
                    VALUES (?, 1, ?)
                    ON CONFLICT(account) DO UPDATE SET 
                        total_submitted = total_submitted + 1,
                        last_submit = ?
                """, (account, datetime.now(), datetime.now()))
                
                # Cập nhật website_stats
                self.conn.execute("""
                    INSERT INTO website_stats (website, total_submitted, last_submit)
                    VALUES (?, 1, ?)
                    ON CONFLICT(website) DO UPDATE SET 
                        total_submitted = total_submitted + 1,
                        last_submit = ?
                """, (website, datetime.now(), datetime.now()))
                
                # Nếu status là SUCCESS hoặc FAILED, cập nhật thêm
                if status == "SUCCESS":
                    self.conn.execute(
                        "UPDATE account_stats SET total_success = total_success + 1 WHERE account = ?",
                        (account,)
                    )
                    self.conn.execute(
                        "UPDATE website_stats SET total_success = total_success + 1 WHERE website = ?",
                        (website,)
                    )
                elif status == "FAILED":
                    self.conn.execute(
                        "UPDATE account_stats SET total_failed = total_failed + 1 WHERE account = ?",
                        (account,)
                    )
                    self.conn.execute(
                        "UPDATE website_stats SET total_failed = total_failed + 1 WHERE website = ?",
                        (website,)
                    )
                
                self.conn.commit()
                logger.debug(f"💾 [{account}] Code {code} ghi lại: {status}")
                
            except sqlite3.IntegrityError:
                # Code đã tồn tại, cập nhật
                self.conn.execute("""
                    UPDATE code_submission 
                    SET status = ?, result = ?, submitted_at = ?
                    WHERE code = ?
                """, (status, result, datetime.now(), code))
                self.conn.commit()
                logger.warning(f"⚠️ Code {code} đã tồn tại, cập nhật record")
            except Exception as e:
                logger.error(f"❌ Lỗi record submission: {e}")
                self.conn.rollback()
    
    def get_code_status(self, code: str) -> Optional[Dict]:
        """Lấy trạng thái của 1 code (thread-safe)"""
        with self._lock:
            try:
                cursor = self.conn.execute(
                    "SELECT * FROM code_submission WHERE code = ?",
                    (code,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"❌ Lỗi get code status: {e}")
                return None
    
    def get_account_stats(self, account: str) -> Optional[Dict]:
        """Lấy thống kê của account (thread-safe)"""
        with self._lock:
            try:
                cursor = self.conn.execute(
                    "SELECT * FROM account_stats WHERE account = ?",
                    (account,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"❌ Lỗi get account stats: {e}")
                return None
    
    def get_all_account_stats(self) -> List[Dict]:
        """Lấy tất cả account stats (thread-safe)"""
        with self._lock:
            try:
                cursor = self.conn.execute(
                    "SELECT * FROM account_stats ORDER BY total_submitted DESC"
                )
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"❌ Lỗi get all account stats: {e}")
                return []
    
    def get_success_rate(self, account: str = None) -> float:
        """Tính tỉ lệ thành công (thread-safe)"""
        with self._lock:
            try:
                if account:
                    cursor = self.conn.execute(
                        "SELECT total_success, total_submitted FROM account_stats WHERE account = ?",
                        (account,)
                    )
                else:
                    cursor = self.conn.execute(
                        "SELECT SUM(total_success) as total_success, SUM(total_submitted) as total_submitted FROM account_stats"
                    )
                row = cursor.fetchone()
                if row and row[1] and row[1] > 0:
                    return (row[0] / row[1]) * 100
                return 0.0
            except Exception as e:
                logger.error(f"❌ Lỗi tính success rate: {e}")
                return 0.0
    
    def print_stats(self):
        """In thống kê toàn bộ (thread-safe)"""
        with self._lock:
            try:
                logger.info("\n" + "="*70)
                logger.info("📊 THỐNG KÊ:")
                
                logger.info("\n📱 ACCOUNT STATS:")
                for stat in self.get_all_account_stats()[:10]:
                    success_rate = (stat['total_success'] / stat['total_submitted'] * 100) if stat['total_submitted'] > 0 else 0
                    logger.info(
                        f"   {stat['account']}: "
                        f"✅ {stat['total_success']} | "
                        f"❌ {stat['total_failed']} | "
                        f"Tổng: {stat['total_submitted']} | "
                        f"Tỉ lệ: {success_rate:.1f}%"
                    )
                
                logger.info("="*70 + "\n")
            except Exception as e:
                logger.error(f"❌ Lỗi print stats: {e}")
    
    def close(self):
        """Đóng database connection (thread-safe)"""
        with self._lock:
            try:
                self.conn.close()
                logger.info("✅ Database đã đóng")
            except Exception as e:
                logger.error(f"❌ Lỗi close database: {e}")


# Global database instance
_db_instance = None

def init_database(db_path: str = "data/code_history.db") -> CodeDatabase:
    """Khởi tạo database (thread-safe)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = CodeDatabase(db_path)
    return _db_instance

def get_database() -> CodeDatabase:
    """Lấy database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = init_database()
    return _db_instance