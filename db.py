import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

        # Create expense table if it doesn't exist
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS expense_record (
                item_name TEXT,
                item_price REAL,
                purchase_date DATE
            )
        """)

        # Create settings table if it doesn't exist
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value REAL
            )
        """)

        # Ensure there is at least one default balance stored
        if self.get_balance() is None:
            self.set_balance(140220.06)

        self.conn.commit()

    # ===== Expense CRUD =====
    def fetch_record(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def insert_record(self, item_name, item_price, purchase_date):
        self.cur.execute("INSERT INTO expense_record VALUES (?, ?, ?)",
                         (item_name, float(item_price), purchase_date))
        self.conn.commit()

    def remove_record(self, rowid):
        self.cur.execute("DELETE FROM expense_record WHERE rowid=?", (rowid,))
        self.conn.commit()

    def update_record(self, item_name, item_price, purchase_date, rowid):
        self.cur.execute("""
            UPDATE expense_record
            SET item_name = ?, item_price = ?, purchase_date = ?
            WHERE rowid = ?
        """, (item_name, float(item_price), purchase_date, rowid))
        self.conn.commit()

    # ===== Balance Management =====
    def get_balance(self):
        self.cur.execute("SELECT value FROM settings WHERE key='initial_balance'")
        row = self.cur.fetchone()
        return row[0] if row else None

    def set_balance(self, value):
        self.cur.execute("""
            INSERT INTO settings (key, value)
            VALUES ('initial_balance', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (float(value),))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
