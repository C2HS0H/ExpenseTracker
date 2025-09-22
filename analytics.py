import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from sklearn.linear_model import LinearRegression


class AnalyticsWindow(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.title("Analytics & Forecast")

        try:
            self.state("zoomed")
        except:
            self.attributes("-zoomed", True)

        main_frame = ttk.Frame(self, padding="5")
        main_frame.pack(expand=True, fill="both")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        prediction_frame = ttk.LabelFrame(
            main_frame, text="Spending Forecast", padding="5"
        )
        prediction_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.prediction_label = ttk.Label(
            prediction_frame, text="Calculating...", font=("Segoe UI", 10, "bold")
        )
        self.prediction_label.pack()

        self.pie_frame = ttk.LabelFrame(
            main_frame, text="Spending by Category", padding="5"
        )
        self.pie_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.line_frame = ttk.LabelFrame(
            main_frame, text="Spending Over Time", padding="5"
        )
        self.line_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.load_data_and_plot()

    def load_data_and_plot(self):
        records = self.db.fetch_record(
            "SELECT item_price, purchase_date, category FROM expense_record"
        )
        if not records:
            self.prediction_label.config(text="Not enough data to create analytics.")
            return

        df = pd.DataFrame(records, columns=["price", "date", "category"])
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["category", "date"])
        df["category"] = df["category"].str.strip().str.title()

        if df.empty:
            self.prediction_label.config(text="No categorized expenses found.")
            return

        self.create_category_bar_chart(df)
        monthly_data = self.create_stacked_monthly_chart(df)
        self.run_prediction(monthly_data)

    def create_category_bar_chart(self, df):
        category_spending = df.groupby("category")["price"].sum().sort_values(ascending=True)
        if category_spending.empty:
            return

        fig = Figure(figsize=(5, 4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)

        ax.barh(category_spending.index, category_spending.values, color="#0078D4")
        ax.set_xlabel("Total Spent (Rs.)", color="white", fontsize=10)
        ax.set_title("Spending by Category", color="white", fontsize=12)
        ax.tick_params(colors="white", labelsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_facecolor("#3c3c3c")
        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def create_stacked_monthly_chart(self, df):
        df_monthly = df.groupby([pd.Grouper(key="date", freq="ME"), "category"])["price"].sum().unstack(fill_value=0)
        df_monthly = df_monthly[df_monthly.sum(axis=1) > 0]

        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)

        bottom = np.zeros(len(df_monthly))
        colors = ["#0078D4", "#FF6F61", "#6A5ACD", "#FFA500", "#2E8B57", "#D2691E"]

        for i, category in enumerate(df_monthly.columns):
            ax.bar(df_monthly.index, df_monthly[category], bottom=bottom, label=category,
                   color=colors[i % len(colors)])
            bottom += df_monthly[category].values

        ax.set_title("Monthly Spending by Category", color="white", fontsize=12)
        ax.set_ylabel("Total Spent (Rs.)", color="white", fontsize=10)
        ax.tick_params(axis="x", colors="white", rotation=45, labelsize=10)
        ax.tick_params(axis="y", colors="white", labelsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_facecolor("#3c3c3c")
        ax.xaxis.set_major_formatter(DateFormatter("%b-%Y"))
        ax.legend(facecolor="#2b2b2b", edgecolor="white", labelcolor="white", fontsize=8)
        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=self.line_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")
        
        return df_monthly.sum(axis=1).reset_index(name="price")

    def run_prediction(self, monthly_data):
        if len(monthly_data) < 2:
            self.prediction_label.config(
                text="Need at least 2 months of data for a forecast."
            )
            return

        X = np.arange(len(monthly_data)).reshape(-1, 1)
        y = monthly_data["price"].values

        model = LinearRegression()
        model.fit(X, y)

        next_month_index = len(monthly_data)
        prediction = model.predict([[next_month_index]])[0]

        self.prediction_label.config(
            text=f"Forecast for Next Month: Rs. {prediction:.2f}", foreground="cyan"
        )
