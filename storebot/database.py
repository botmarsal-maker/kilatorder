import sqlite3
import os
import datetime

class Database:
    def __init__(self, db_file):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_produk TEXT,
                harga INTEGER,
                stok INTEGER,
                kategori TEXT,
                deskripsi TEXT
            )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                harga INTEGER,
                tanggal TEXT
            )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS vouchers (
                kode TEXT PRIMARY KEY,
                nominal INTEGER,
                batas_penggunaan INTEGER,
                terpakai INTEGER DEFAULT 0,
                tanggal_kadaluarsa TEXT
            )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                tanggal TEXT
            )''')

    def get_user(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if not user:
            with self.conn:
                self.conn.execute("INSERT INTO users (id, balance) VALUES (?, 0)", (user_id,))
            return {"id": user_id, "balance": 0}
        return dict(user)

    def update_balance(self, user_id, amount):
        with self.conn:
            self.conn.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))

    def get_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM products")
        return [dict(row) for row in cur.fetchall()]

    def get_product(self, product_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def update_stock(self, product_id, amount):
        with self.conn:
            self.conn.execute("UPDATE products SET stok = stok + ? WHERE id = ?", (amount, product_id))

    def add_transaction(self, user_id, product_id, harga):
        with self.conn:
            self.conn.execute("INSERT INTO transactions (user_id, product_id, harga, tanggal) VALUES (?, ?, ?, ?)",
                              (user_id, product_id, harga, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def check_voucher(self, kode):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM vouchers WHERE kode = ?", (kode,))
        row = cur.fetchone()
        return dict(row) if row else None
        
    def use_voucher(self, kode):
        with self.conn:
            self.conn.execute("UPDATE vouchers SET terpakai = terpakai + 1 WHERE kode = ?", (kode,))

    def add_deposit(self, user_id, amount):
        with self.conn:
            cur = self.conn.execute("INSERT INTO deposits (user_id, amount, tanggal) VALUES (?, ?, ?)",
                              (user_id, amount, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            return cur.lastrowid

    def get_deposit(self, deposit_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def update_deposit_status(self, deposit_id, status):
        with self.conn:
            self.conn.execute("UPDATE deposits SET status = ? WHERE id = ?", (status, deposit_id))

    def add_product(self, nama, harga, stok, kategori, deskripsi):
        with self.conn:
            self.conn.execute("INSERT INTO products (nama_produk, harga, stok, kategori, deskripsi) VALUES (?, ?, ?, ?, ?)",
                              (nama, harga, stok, kategori, deskripsi))

    def edit_product(self, product_id, nama, harga, stok, kategori, deskripsi):
        with self.conn:
            self.conn.execute('''UPDATE products 
                SET nama_produk=?, harga=?, stok=?, kategori=?, deskripsi=? 
                WHERE id=?''', (nama, harga, stok, kategori, deskripsi, product_id))

    def delete_product(self, product_id):
        with self.conn:
            self.conn.execute("DELETE FROM products WHERE id=?", (product_id,))

    def get_all_users(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users")
        return [dict(row) for row in cur.fetchall()]

    def get_all_transactions(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 50")
        return [dict(row) for row in cur.fetchall()]
