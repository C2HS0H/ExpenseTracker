import sqlite3
import datetime as dt


class Database:
    def __init__(self, db="expenses.db"):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_record (
            item_name TEXT NOT NULL,
            item_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            category TEXT
        )
        """)
        
        self.create_monthly_budget_table()
        self.conn.commit()

    def create_monthly_budget_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_budget (
            month TEXT PRIMARY KEY,
            budget REAL NOT NULL
        )
        """)
        self.conn.commit()

    def insert_record(self, item_name, item_price, purchase_date, category):
        self.cursor.execute("""
        INSERT INTO expense_record (item_name, item_price, purchase_date, category)
        VALUES (?, ?, ?, ?)
        """, (item_name, item_price, purchase_date, category))
        self.conn.commit()

    def fetch_record(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update_record(self, item_name, item_price, purchase_date, category, rowid):
        self.cursor.execute("""
        UPDATE expense_record
        SET item_name = ?, item_price = ?, purchase_date = ?, category = ?
        WHERE rowid = ?
        """, (item_name, item_price, purchase_date, category, rowid))
        self.conn.commit()

    def remove_record(self, rowid):
        self.cursor.execute("DELETE FROM expense_record WHERE rowid = ?", (rowid,))
        self.conn.commit()

    def set_monthly_budget(self, amount):
        month = dt.datetime.now().strftime("%Y-%m")
        self.cursor.execute("""
        INSERT INTO monthly_budget (month, budget)
        VALUES (?, ?)
        ON CONFLICT(month) DO UPDATE SET budget=excluded.budget
        """, (month, amount))
        self.conn.commit()

    def get_monthly_budget(self):
        month = dt.datetime.now().strftime("%Y-%m")
        self.cursor.execute("SELECT budget FROM monthly_budget WHERE month = ?", (month,))
        row = self.cursor.fetchone()
        return row[0] if row else 0.0

    def get_monthly_remaining_balance(self):
        month = dt.datetime.now().strftime("%Y-%m")
        budget = self.get_monthly_budget()
        self.cursor.execute("""
        SELECT SUM(item_price) FROM expense_record
        WHERE strftime('%Y-%m', purchase_date) = ?
        """, (month,))
        spent = self.cursor.fetchone()[0] or 0.0
        remaining = budget - spent
        return remaining, budget, spent

    def close(self):
        self.conn.close()
