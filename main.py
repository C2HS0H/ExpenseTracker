import datetime as dt
import tkinter as tk
import sv_ttk
from tkinter import messagebox, ttk, filedialog
import tkinter.simpledialog as sd
import requests
from tkcalendar import DateEntry

from db import Database
from autocomplete import AutocompleteEntry
from analytics import AnalyticsWindow


class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("900x720")
        self.resizable(False, False)

        self.db = Database(db="expenses.db")
        self.db.create_monthly_budget_table()  

        self.selected_rowid = 0
        self.categories = [
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health",
            "Groceries",
            "Education",
            "Other",
        ]

        sv_ttk.set_theme("dark")

        self.create_widgets()
        self.after(10, self.configure_styles)
        self.after(50, self.refresh_data)

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TEntry", padding=4, font=("Segoe UI", 10))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        emoji_font = ("Segoe UI Emoji", 10)
        style.configure("Emoji.TButton", font=emoji_font, padding=6)

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.tbl = ttk.Treeview(
            frame,
            columns=("Serial no", "Item Name", "Price", "Purchase Date", "Category"),
            show="headings",
        )
        self.tbl.heading("Serial no", text="Serial no")
        self.tbl.heading("Item Name", text="Item Name")
        self.tbl.heading("Price", text="Price")
        self.tbl.heading("Purchase Date", text="Purchase Date")
        self.tbl.heading("Category", text="Category")
        self.tbl.column("Serial no", width=70, anchor="center")
        self.tbl.column("Item Name", width=180, anchor="w")
        self.tbl.column("Price", width=120, anchor="e")
        self.tbl.column("Purchase Date", width=120, anchor="center")
        self.tbl.column("Category", width=120, anchor="center")
        self.tbl.bind("<ButtonRelease-1>", self.select_record)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tbl.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tbl.xview)
        self.tbl.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tbl.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        input_frame = ttk.LabelFrame(self, text="Add / Update Expense", padding=8)
        input_frame.pack(pady=8, padx=20, fill="x")

        left_frame = ttk.Frame(input_frame)
        left_frame.grid(row=0, column=0, padx=8, pady=4, sticky="n")

        INPUT_FIELD_WIDTH = 28
        ttk.Label(left_frame, text="Item Name").grid(row=0, column=0, padx=8, pady=4, sticky="w")
        previous_items = [rec[0] for rec in self.db.fetch_record("SELECT DISTINCT item_name FROM expense_record")]
        self.item_name_entry = AutocompleteEntry(left_frame, suggestions=previous_items, width=INPUT_FIELD_WIDTH)
        self.item_name_entry.grid(row=0, column=1, padx=8, pady=4, sticky="w")

        ttk.Label(left_frame, text="Price").grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self.item_amt_entry = ttk.Entry(left_frame, width=INPUT_FIELD_WIDTH)
        self.item_amt_entry.grid(row=1, column=1, padx=8, pady=4, sticky="w")

        ttk.Label(left_frame, text="Category").grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self.category_entry = ttk.Combobox(left_frame, values=self.categories, width=INPUT_FIELD_WIDTH - 4)
        self.category_entry.grid(row=2, column=1, padx=8, pady=4, sticky="w")
        self.category_entry.set("Other")

        ttk.Label(left_frame, text="Purchase Date").grid(row=3, column=0, padx=8, pady=4, sticky="w")
        self.transaction_date_entry = DateEntry(left_frame, width=INPUT_FIELD_WIDTH - 4, date_pattern="yyyy-mm-dd")
        self.transaction_date_entry.grid(row=3, column=1, padx=8, pady=4, sticky="w")
        self.transaction_date_entry.set_date(dt.datetime.now())
        self.style_datepicker()

        ttk.Separator(input_frame, orient="vertical").grid(row=0, column=1, sticky="ns", padx=15, pady=5)

        right_frame = ttk.Frame(input_frame)
        right_frame.grid(row=0, column=2, padx=8, pady=4, sticky="n")
        ttk.Label(right_frame, text="OR").pack(pady=4)
        ttk.Button(right_frame, text="📷 Upload Receipt", style="Emoji.TButton", width=20, command=self.upload_receipt).pack(pady=8)

        btn_width = 14
        button_frame = ttk.Frame(self, padding=8)
        button_frame.pack(pady=8)

        ttk.Button(button_frame, text="💾 Save Record", style="Emoji.TButton", width=btn_width, command=self.save_record).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(button_frame, text="🧹 Clear Entry", style="Emoji.TButton", width=btn_width, command=self.clear_entries).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(button_frame, text="📝 Update", style="Emoji.TButton", width=btn_width, command=self.update_record).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(button_frame, text="❌ Delete", style="Emoji.TButton", width=btn_width, command=self.delete_record).grid(row=0, column=3, padx=4, pady=4)

        ttk.Button(button_frame, text="📆 Current Date", style="Emoji.TButton", width=btn_width, command=self.set_date).grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(button_frame, text="💳 Total Spent", style="Emoji.TButton", width=btn_width, command=self.show_total_spent).grid(row=1, column=1, padx=4, pady=4)
        ttk.Button(button_frame, text="💰 Balance", style="Emoji.TButton", width=btn_width, command=self.balance_options).grid(row=1, column=2, padx=4, pady=4)
        ttk.Button(button_frame, text="📊 Analytics", style="Emoji.TButton", width=btn_width, command=self.open_analytics_window).grid(row=1, column=3, padx=4, pady=4)

        self.status_label = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def style_datepicker(self):
        self.transaction_date_entry.configure(background="#2b2b2b", borderwidth=0)
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
            weekendforeground="#cccccc",
        )

    def open_analytics_window(self):
        AnalyticsWindow(self, self.db)

    def validate_form(self):
        if not self.item_name_entry.get():
            messagebox.showerror("Validation Error", "Item Name cannot be empty.")
            return False
        try:
            float(self.item_amt_entry.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Item Price must be a valid number.")
            return False
        if not self.category_entry.get():
            messagebox.showerror("Validation Error", "Please select or enter a Category.")
            return False
        if not self.transaction_date_entry.get():
            messagebox.showerror("Validation Error", "Please select a Purchase Date.")
            return False
        return True

    def save_record(self):
        if self.validate_form():
            item_name = self.item_name_entry.get()
            item_price = self.item_amt_entry.get()
            category = self.category_entry.get()
            purchase_date = self.transaction_date_entry.get()

            self.db.insert_record(item_name, float(item_price), purchase_date, category)
            self.clear_entries()
            self.refresh_data()
            self.status_label.config(text="✅ Record saved successfully", foreground="green")

            if item_name not in self.item_name_entry.suggestions:
                self.item_name_entry.suggestions.append(item_name)
            if category not in self.category_entry["values"]:
                self.category_entry["values"] = list(self.category_entry["values"]) + [category]

    def set_date(self):
        self.transaction_date_entry.set_date(dt.datetime.now())

    def clear_entries(self):
        self.selected_rowid = 0
        self.item_name_entry.clear()
        self.item_amt_entry.delete(0, "end")
        self.category_entry.set("Other")
        self.set_date()
        self.item_name_entry.focus()

    def refresh_data(self):
        self.tbl.delete(*self.tbl.get_children())
        for idx, rec in enumerate(self.db.fetch_record("SELECT rowid, * FROM expense_record"), start=1):
            price = rec[2] if rec[2] is not None else 0.0
            self.tbl.insert(parent="", index="end", iid=rec[0], values=(idx, rec[1], f"{price:.2f}", rec[3], rec[4]))

    def balance_options(self):
        choice = messagebox.askquestion(
            "Balance Options",
            "Do you want to set a new monthly budget?\nClick 'Yes' to set, 'No' to view remaining balance.",
        )
        if choice == "yes":
            self.set_balance()
        else:
            self.show_balance()

    def update_record(self):
        if self.selected_rowid == 0:
            messagebox.showerror("Error", "Please select a record to update")
            return
        if self.validate_form():
            self.db.update_record(
                self.item_name_entry.get(),
                float(self.item_amt_entry.get()),
                self.transaction_date_entry.get(),
                self.category_entry.get(),
                self.selected_rowid,
            )
            self.clear_entries()
            self.refresh_data()
            self.status_label.config(text="✅ Record updated successfully", foreground="green")

    def delete_record(self):
        if self.selected_rowid == 0:
            messagebox.showerror("Error", "Please select a record to delete")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            self.db.remove_record(self.selected_rowid)
            self.clear_entries()
            self.refresh_data()
            self.status_label.config(text="✅ Record deleted successfully", foreground="green")

    def show_total_spent(self):
        total_spent = sum(rec[0] for rec in self.db.fetch_record("SELECT item_price FROM expense_record"))
        messagebox.showinfo("Total Spent", f"Total Expenses: Rs. {total_spent:.2f}")

    def show_balance(self):
        remaining, monthly_budget, spent = self.db.get_monthly_remaining_balance()
        messagebox.showinfo(
            "Monthly Budget",
            f"Monthly Budget: Rs. {monthly_budget:.2f}\n"
            f"Total Spent: Rs. {spent:.2f}\n"
            f"Remaining Balance: Rs. {remaining:.2f}"
        )

    def set_balance(self):
        try:
            new_budget = sd.askfloat(
                "Set Monthly Budget",
                "Enter new monthly budget:",
                minvalue=0
            )
            if new_budget is not None:
                self.db.set_monthly_budget(new_budget)
                self.status_label.config(text=f"✅ Monthly budget set: Rs. {new_budget:.2f}", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def select_record(self, event):
        selected_items = self.tbl.selection()
        if not selected_items:
            self.selected_rowid = 0
            return
        selected_item_iid = selected_items[0]
        self.selected_rowid = int(selected_item_iid)
        values = self.tbl.item(selected_item_iid)["values"]
        self.item_name_entry.set_text(values[1])
        self.item_amt_entry.delete(0, "end")
        self.item_amt_entry.insert(0, values[2])
        self.transaction_date_entry.set_date(values[3])
        self.category_entry.set(values[4])

    def upload_receipt(self):
        try:
            file_path = filedialog.askopenfilename(title="Select a receipt image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
            if not file_path:
                return
            self.status_label.config(text="📤 Uploading receipt...", foreground="blue")
            self.update_idletasks()
            r = requests.post(
                "https://ocr.asprise.com/api/v1/receipt",
                data={"client_id": "TEST", "recognizer": "auto", "ref_no": "ocr_python_ui"},
                files={"file": open(file_path, "rb")},
            )
            if r.status_code != 200:
                self.status_label.config(text="❌ OCR API Error", foreground="red")
                messagebox.showerror("OCR Error", f"Failed to contact OCR API.\nStatus: {r.status_code}")
                return
            result = r.json()
            if not result.get("success", False):
                self.status_label.config(text="❌ OCR failed", foreground="red")
                messagebox.showerror("OCR Error", "OCR failed. Try another image.")
                return
            receipts = result.get("receipts", [])
            if not receipts:
                self.status_label.config(text="❌ No receipts found", foreground="red")
                messagebox.showerror("OCR Error", "No receipts detected in image.")
                return
            rec = receipts[0]
            items = rec.get("items", [])
            date = rec.get("date", str(dt.datetime.now().date()))
            if not items:
                self.status_label.config(text="❌ No items found", foreground="red")
                messagebox.showerror("OCR Error", "No items found in receipt.")
                return
            for item in items:
                desc = item.get("description", "Unknown Item")
                amt = item.get("amount", 0.0)
                self.db.insert_record(desc, amt, date, "Other")
                if desc not in self.item_name_entry.suggestions:
                    self.item_name_entry.suggestions.append(desc)
            self.refresh_data()
            messagebox.showinfo("Success", f"OCR completed.\nAdded {len(items)} items from receipt.")
            self.status_label.config(text=f"✅ Added {len(items)} items from receipt", foreground="green")
        except requests.exceptions.RequestException as e:
            self.status_label.config(text="❌ Connection Error", foreground="red")
            messagebox.showerror("Connection Error", f"Could not reach OCR API.\n{e}")
        except Exception as e:
            self.status_label.config(text="❌ Unexpected Error", foreground="red")
            messagebox.showerror("Unexpected Error", f"Something went wrong:\n{e}")


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
