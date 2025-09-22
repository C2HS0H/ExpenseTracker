# 💰 Daily Expense Tracker

A simple desktop application built with **Python (Tkinter)** to help you manage your daily expenses.  
You can add, update, and delete expenses, view your total spending, check your remaining balance, and analyze your expenses with interactive charts — all in a clean, modern UI.

<div align="center">
<img src="https://i.ibb.co/SD4pb41D/python-klsf-Mn2c-PW.png" width="500" height="400"/>
<img src="https://i.ibb.co/sdNMdDPz/python-4-Mo-G7-MN9gs.png" width="650" height="360"/>
</div>

---

## ✨ Features

- Add / update / delete expense records
- View all expenses in a table with serial numbers, item names, prices, dates, and categories
- Total spent & monthly balance check with one click (balance will not show negative)
- Upload receipt images and auto-extract items using OCR
- Persistent storage using **SQLite**
- Analytics & Forecast window:
  - **Pie chart**: Spending by category
  - **Line chart**: Monthly spending trends
  - **Prediction**: Forecast next month’s expenses using linear regression
- Beautiful dark theme UI with emoji buttons
- Autocomplete for item names
- Cross-platform (Windows, macOS, Linux)

---

## 🚀 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/C2HS0H/ExpenseTracker.git
   cd ExpenseTracker
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python main.py
   ```

## 📦 Build as EXE (Windows)

You can package the app into a standalone `.exe` using **PyInstaller**:

```bash
pyinstaller --onefile --windowed --collect-all babel --collect-all tkcalendar main.py
```

The executable will be available in the `dist/` folder.

---

## 📄 License

This project is licensed under the MIT License — feel free to use and modify it.
