import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "harbi.db"

def get_db():
    """الحصول على اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """إنشاء جميع الجداول المطلوبة"""
    conn = get_db()
    cursor = conn.cursor()
    
    # جدول المستخدمين الرئيسي
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            points INTEGER DEFAULT 0,
            balance INTEGER DEFAULT 0,
            referrer_id INTEGER DEFAULT NULL,
            referral_code TEXT UNIQUE,
            last_daily DATE DEFAULT NULL,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_banned INTEGER DEFAULT 0,
            total_spent_points INTEGER DEFAULT 0,
            total_purchases INTEGER DEFAULT 0
        )
    ''')
    
    # جدول سجل المعاملات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount INTEGER,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول المشتريات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id TEXT,
            product_name TEXT,
            price_points INTEGER,
            price_balance INTEGER,
            details TEXT,
            status TEXT DEFAULT 'pending',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول أكواد الخصم
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            code TEXT PRIMARY KEY,
            points INTEGER,
            uses_left INTEGER,
            expires DATE
        )
    ''')
    
    # جدول طلبات السحب
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            method TEXT,
            account_info TEXT,
            status TEXT DEFAULT 'pending',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ===================== دوال المستخدمين =====================

def get_user(user_id):
    """الحصول على بيانات مستخدم معين"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(user_id, username, first_name, referrer_id=None):
    """إنشاء مستخدم جديد"""
    conn = get_db()
    referral_code = f"HARBI{user_id}{random.randint(100,999)}"
    
    conn.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, referral_code, referrer_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, referral_code, referrer_id))
    
    # مكافأة الإحالة
    if referrer_id:
        referrer = get_user(referrer_id)
        if referrer and not referrer['is_banned']:
            conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (REFERRAL_REWARD, referrer_id))
            conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (REFERRED_REWARD, user_id))
            conn.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'referral', ?, ?)", 
                        (referrer_id, REFERRAL_REWARD, f"إحالة مستخدم جديد {user_id}"))
            conn.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'referral', ?, ?)", 
                        (user_id, REFERRED_REWARD, "مكافأة تسجيل عبر رابط إحالة"))
    
    conn.commit()
    conn.close()

def update_points(user_id, points, desc):
    """تحديث نقاط المستخدم"""
    conn = get_db()
    conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    if points < 0:
        conn.execute("UPDATE users SET total_spent_points = total_spent_points + ? WHERE user_id = ?", (abs(points), user_id))
    conn.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'points', ?, ?)", 
                (user_id, points, desc))
    conn.commit()
    conn.close()

def update_balance(user_id, amount, desc):
    """تحديث رصيد المستخدم"""
    conn = get_db()
    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'balance', ?, ?)", 
                (user_id, amount, desc))
    conn.commit()
    conn.close()

def claim_daily(user_id):
    """تسجيل المكافأة اليومية"""
    conn = get_db()
    today = datetime.now().date()
    user = get_user(user_id)
    if user and user['last_daily'] != str(today):
        conn.execute("UPDATE users SET points = points + ?, last_daily = ? WHERE user_id = ?", 
                    (DAILY_REWARD, today, user_id))
        conn.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'daily', ?, ?)", 
                    (user_id, DAILY_REWARD, "مكافأة يومية"))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_leaderboard(limit=10):
    """الحصول على ترتيب المستخدمين حسب النقاط"""
    conn = get_db()
    users = conn.execute("SELECT user_id, username, first_name, points, balance FROM users WHERE is_banned = 0 ORDER BY points DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return users

def get_user_transactions(user_id, limit=20):
    """الحصول على سجل معاملات المستخدم"""
    conn = get_db()
    transactions = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return transactions

def get_all_users_count():
    """عدد المستخدمين الكلي"""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    conn.close()
    return count

def get_total_points():
    """مجموع النقاط في النظام"""
    conn = get_db()
    total = conn.execute("SELECT SUM(points) as total FROM users").fetchone()['total'] or 0
    conn.close()
    return total

def ban_user(user_id):
    """حظر مستخدم"""
    conn = get_db()
    conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    """إلغاء حظر مستخدم"""
    conn = get_db()
    conn.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
