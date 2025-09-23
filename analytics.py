import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
import datetime as dt


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

        prediction_frame = ttk.LabelFrame(main_frame, text="Spending Forecast", padding="5")
        prediction_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.prediction_label = ttk.Label(prediction_frame, text="Calculating...", font=("Segoe UI", 10, "bold"))
        self.prediction_label.pack()

        self.category_frame = ttk.LabelFrame(main_frame, text="Spending by Category", padding="5")
        self.category_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.line_frame = ttk.LabelFrame(main_frame, text="Monthly Spending Forecast", padding="5")
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
        self.create_monthly_line_chart(df)

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

        canvas = FigureCanvasTkAgg(fig, master=self.category_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def create_monthly_line_chart(self, df):
        df_monthly = df.groupby(pd.Grouper(key="date", freq="ME"))["price"].sum().reset_index()
        df_monthly = df_monthly[df_monthly["price"] > 0]

        df_for_model = df_monthly.copy()

        today = pd.to_datetime(dt.date.today())

        if not df_for_model.empty:
            last_month_in_data = df_for_model['date'].max()

            if last_month_in_data.year == today.year and last_month_in_data.month == today.month:

                df_for_model = df_for_model.iloc[:-1]

        future_months = 3
        forecast_dates, forecast_values = self.get_forecasts(df_for_model, future_months)

        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)

        if not df_for_model.empty:
            ax.plot(df_for_model["date"], df_for_model["price"], marker="o", color="#C81B5A", label="Actual Spending")

        if forecast_values and not df_for_model.empty:
            last_complete_date = df_for_model["date"].iloc[-1]
            last_complete_price = df_for_model["price"].iloc[-1]

            ax.plot(
                [last_complete_date] + forecast_dates,
                [last_complete_price] + forecast_values,
                marker="o",
                linestyle="--",
                color="orange",
                label="Forecast"
            )
        elif forecast_values and df_for_model.empty:

            ax.plot(
                forecast_dates,
                forecast_values,
                marker="o",
                linestyle="--",
                color="orange",
                label="Forecast"
            )

        ax.set_title("Monthly Spending Forecast", color="white", fontsize=12)
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

    def get_forecasts(self, monthly_data, future_months=3):
        forecast_dates = []
        forecast_values = []

        history = monthly_data.copy()

        if history.empty:
            return [], []

        for i in range(future_months):
            pred = self.run_prediction(history, update_label=(i==0))
            if pred is None:
                break

            pred = max(pred, 0)
            next_date = history["date"].max() + pd.offsets.MonthEnd()
            forecast_dates.append(next_date)
            forecast_values.append(pred)

            new_row = pd.DataFrame({"date": [next_date], "price": [pred]})
            history = pd.concat([history, new_row], ignore_index=True)

        return forecast_dates, forecast_values

    def run_prediction(self, monthly_data, update_label=True):
        n_months = len(monthly_data)
        prediction = None
        model_used = None

        if n_months < 2:
            if update_label:
                self.prediction_label.config(text="Need at least 2 months of complete data for a forecast.")
            return None

        if n_months < 6:
            X = np.arange(n_months).reshape(-1, 1)
            y = monthly_data["price"].values
            model = LinearRegression().fit(X, y)
            prediction = model.predict([[n_months]])[0]
            model_used = "Linear Regression"

        elif 6 <= n_months < 12:
            series = monthly_data.set_index("date")["price"]
            if series.index.freq is None:
                series.index.freq = 'ME'
            model = ExponentialSmoothing(series, trend="add", seasonal=None).fit()
            prediction = model.forecast(1).iloc[0]
            model_used = "Holt-Winters (Trend)"

        elif 12 <= n_months < 18:
            series = monthly_data.set_index("date")["price"]
            if series.index.freq is None:
                series.index.freq = 'ME'
            model = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=12).fit()
            prediction = model.forecast(1).iloc[0]
            model_used = "Holt-Winters (Trend + Seasonality)"

        else:
            df = monthly_data.rename(columns={"date": "ds", "price": "y"})
            model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            model.fit(df)
            future = model.make_future_dataframe(periods=1, freq='M')
            forecast = model.predict(future)
            prediction = forecast.iloc[-1]["yhat"]
            model_used = "Prophet"

        if prediction is not None:
            prediction = max(prediction, 0)

        if update_label and prediction is not None:
            self.prediction_label.config(
                text=f"Forecast for Next Month: Rs. {prediction:.2f}\nModel used: {model_used}",
                foreground="cyan",
            )

        return prediction