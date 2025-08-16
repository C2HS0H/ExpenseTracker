# 💰 Daily Expense Tracker

A simple desktop application built with **Python (Tkinter)** to help you manage your daily expenses.  
You can add, update, and delete expenses, view your total spending, and check your remaining balance — all in a clean, modern UI.

<div align="center">
<img src="https://i.ibb.co/SDSvLHfk/Expense-Tracker-d5-CCo-NG770.png" width="500" height="500"/>
</div>

---


## ✨ Features
- Add / update / delete expense records  
- View all expenses in a table with serial numbers, item names, prices, and dates  
- Total spent & balance check with one click  
- Persistent storage using **SQLite**
- Beautiful dark theme UI with emoji buttons  
- Cross-platform (Windows, macOS, Linux)

---

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ExpenseTracker.git
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

