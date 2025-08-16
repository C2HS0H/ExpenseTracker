import sys
import subprocess
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.simpledialog as sd

try:
    import sv_ttk
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sv_ttk"])
    import sv_ttk

try:
    from tkcalendar import DateEntry
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tkcalendar"])
    from tkcalendar import DateEntry

from db import Database


class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("1000x850")
        self.resizable(False, False)

        # DB object
        self.db = Database(db="expenses.db")

        # Global state
        self.selected_rowid = 0
        self.initial_balance = self.db.get_balance()  # Load from DB

        # Apply dark theme
        sv_ttk.set_theme("dark")

        self.create_widgets()
        self.after(10, self.configure_styles)
        self.after(50, self.refresh_data)

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TButton", padding=8, font=("Segoe UI", 12))
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TEntry", padding=5, font=("Segoe UI", 12))
        style.configure("Treeview", font=("Segoe UI", 12), rowheight=32)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"))
        emoji_font = ("Segoe UI Emoji", 12)
        style.configure("Emoji.TButton", font=emoji_font, padding=8)

    def create_widgets(self):
        # Table frame
        frame = ttk.Frame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.tbl = ttk.Treeview(frame, columns=("Serial no", "Item Name", "Price", "Purchase Date"), show='headings')
        self.tbl.heading("Serial no", text="Serial no")
        self.tbl.heading("Item Name", text="Item Name")
        self.tbl.heading("Price", text="Price")
        self.tbl.heading("Purchase Date", text="Purchase Date")
        self.tbl.column("Serial no", width=80, anchor="center")
        self.tbl.column("Item Name", width=200, anchor="w")
        self.tbl.column("Price", width=150, anchor="e")
        self.tbl.column("Purchase Date", width=150, anchor="center")
        self.tbl.pack(side="left", fill="both", expand=True)
        self.tbl.bind("<ButtonRelease-1>", self.select_record)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tbl.yview)
        scrollbar.pack(side="right", fill="y")
        self.tbl.configure(yscrollcommand=scrollbar.set)

        # Input frame
        input_frame = ttk.LabelFrame(self, text="Add / Update Expense", padding=10)
        input_frame.pack(pady=10, padx=20, fill="x")

        INPUT_FIELD_WIDTH = 30

        ttk.Label(input_frame, text="Item Name").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.item_name_entry = ttk.Entry(input_frame, width=INPUT_FIELD_WIDTH)
        self.item_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(input_frame, text="Price").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.item_amt_entry = ttk.Entry(input_frame, width=INPUT_FIELD_WIDTH)
        self.item_amt_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(input_frame, text="Purchase Date").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.transaction_date_entry = DateEntry(
            input_frame,
            width=INPUT_FIELD_WIDTH-4,
            date_pattern='yyyy-mm-dd'
        )
        self.transaction_date_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.transaction_date_entry.set_date(dt.datetime.now())
        self.style_datepicker()

        # Buttons frame
        btn_width = 18
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(pady=10)

        # Row 0
        ttk.Button(button_frame, text="💾 Save Record", style="Emoji.TButton", width=btn_width, command=self.save_record).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="🧹 Clear Entry", style="Emoji.TButton", width=btn_width, command=self.clear_entries).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="📝 Update", style="Emoji.TButton", width=btn_width, command=self.update_record).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="❌ Delete", style="Emoji.TButton", width=btn_width, command=self.delete_record).grid(row=0, column=3, padx=5, pady=5)
        
        # Row 1
        ttk.Button(button_frame, text="📆 Current Date", style="Emoji.TButton", width=btn_width, command=self.set_date).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="💳 Total Spent", style="Emoji.TButton", width=btn_width, command=self.show_total_spent).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="🏦 Set Balance", style="Emoji.TButton", width=btn_width, command=self.set_balance).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="💰 Show Balance", style="Emoji.TButton", width=btn_width, command=self.show_balance).grid(row=1, column=3, padx=5, pady=5)
        # Status bar
        self.status_label = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def style_datepicker(self):
        self.transaction_date_entry.configure(
            background="#2b2b2b",
            borderwidth=0
        )
        self.transaction_date_entry._top_cal.configure(background="#2b2b2b")
        cal = self.transaction_date_entry._calendar
        cal.configure(
            background="#2b2b2b",
            disabledbackground="#2b2b2b",
            bordercolor="#2b2b2b",
            headersbackground="#1e1e1e",
            normalbackground="#2b2b2b",
            weekendbackground="#2b2b2b",
            selectbackground="#0078D4",
            selectforeground="white",
            normalforeground="white",
            weekendforeground="#cccccc"
        )

    # ===== Core Functions =====
    def validate_form(self):
        if not self.item_name_entry.get():
            messagebox.showerror("Validation Error", "Item Name cannot be empty.")
            return False
        try:
            float(self.item_amt_entry.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Item Price must be a valid number.")
            return False
        if not self.transaction_date_entry.get():
            messagebox.showerror("Validation Error", "Please select a Purchase Date.")
            return False
        return True

    def save_record(self):
        if self.validate_form():
            self.db.insert_record(
                item_name=self.item_name_entry.get(),
                item_price=self.item_amt_entry.get(),
                purchase_date=self.transaction_date_entry.get()
            )
            self.clear_entries()
            self.refresh_data()
            self.status_label.config(text="✅ Record saved successfully", foreground="green")

    def set_date(self):
        self.transaction_date_entry.set_date(dt.datetime.now())

    def clear_entries(self):
        self.item_name_entry.delete(0, 'end')
        self.item_amt_entry.delete(0, 'end')
        self.transaction_date_entry.delete(0, 'end')

    def refresh_data(self):
        self.tbl.delete(*self.tbl.get_children())
        self.count = 0
        for rec in self.db.fetch_record("select rowid,* from expense_record"):
            rounded_price = round(rec[2], 2) if rec[2] is not None else 0.0
            self.tbl.insert(
                parent="",
                index="end",
                iid=self.count,
                values=(rec[0], rec[1], rounded_price, rec[3])
            )
            self.count += 1
        self.after(500, self.refresh_data)

    def update_record(self):
        if self.selected_rowid == 0:
            messagebox.showerror("Error", "Please select a record to update")
            return
        if self.validate_form():
            self.db.update_record(
                self.item_name_entry.get(),
                self.item_amt_entry.get(),
                self.transaction_date_entry.get(),
                self.selected_rowid
            )
            self.clear_entries()
            self.refresh_data()
            self.status_label.config(text="✅ Record updated successfully", foreground="green")

    def delete_record(self):
        if self.selected_rowid == 0:
            messagebox.showerror("Error", "Please select a record to delete")
            return
        self.db.remove_record(self.selected_rowid)
        self.clear_entries()
        self.refresh_data()
        self.status_label.config(text="✅ Record deleted successfully", foreground="green")

    def show_total_spent(self):
        total_spent = sum(rec[0] for rec in self.db.fetch_record("select item_price from expense_record"))
        rounded_total = round(total_spent, 2)
        messagebox.showinfo("Total Spent", f"Total Expenses: Rs. {rounded_total:.2f}")

    def show_balance(self):
        # Always fetch the latest from DB
        initial_balance = self.db.get_balance()
        total_spent = sum(rec[0] for rec in self.db.fetch_record("select item_price from expense_record"))
        remaining_balance = initial_balance - total_spent
        rounded_balance = round(remaining_balance, 2)
        messagebox.showinfo("Total Balance", f"Balance Remaining: Rs. {rounded_balance:.2f}")

    def set_balance(self):
        try:
            new_balance = sd.askfloat("Set Balance", "Enter new starting balance:",
                                      initialvalue=self.db.get_balance(), minvalue=0)
            if new_balance is not None:
                self.db.set_balance(new_balance)
                self.initial_balance = new_balance
                self.status_label.config(text=f"✅ Balance updated to Rs. {new_balance:.2f}", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def select_record(self, event):
        selected_item = self.tbl.selection()[0]
        self.selected_rowid = self.tbl.item(selected_item)['values'][0]
        self.clear_entries()
        self.item_name_entry.insert(0, self.tbl.item(selected_item)['values'][1])
        self.item_amt_entry.insert(0, self.tbl.item(selected_item)['values'][2])
        self.transaction_date_entry.insert(0, self.tbl.item(selected_item)['values'][3])


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
