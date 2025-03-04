#!/usr/local/bin/python3

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from binance.spot import Spot
import matplotlib.dates as mdates


def get_alltime(time):
    formatted_time = datetime.datetime.fromtimestamp(float(time / 1000))
    return formatted_time.strftime('%Y-%m-%d %H:%M:%S')


def parser_klines(klines):
    return {
        "Open_time": klines[0],
        "Open": klines[1],
        "High": klines[2],
        "Low": klines[3],
        "Close": klines[4],
        "Volume": klines[5],
        "Close_time": klines[6],
        "Quote_asset_volume": klines[7],
        "Number_of_trades": klines[8],
        "Taker_buy_base_asset_volume": klines[9],
        "Taker_buy_quote_asset_volume": klines[10],
        "Ignore": klines[11]
    }


class TradingBot:
    def __init__(self, symbol, interval="4h", limit=1000):
        self.symbol = symbol
        self.interval = interval
        self.client = Spot()
        self.limit = limit
        self.data = self.fetch_data()
        self.calculate_macd()
        self.indicators = self.calculate_indicators()

    def fetch_data(self):
        try:
            klines = self.client.klines(self.symbol, self.interval, limit=self.limit)
            data = {
                "Open": [], "High": [], "Low": [], "Close": [],
                "Time": [], "Volume": [], "Open_time": [], "Close_time": []
            }

            for kline in klines:
                parsed_kline = parser_klines(kline)
                data["Open"].append(float(parsed_kline["Open"]))
                data["High"].append(float(parsed_kline["High"]))
                data["Low"].append(float(parsed_kline["Low"]))
                data["Close"].append(float(parsed_kline["Close"]))
                data["Time"].append(float(parsed_kline["Close_time"]) / 1000)
                data["Open_time"].append(get_alltime(parsed_kline["Open_time"]))
                data["Close_time"].append(get_alltime(parsed_kline["Close_time"]))
                data["Volume"].append(float(parsed_kline["Volume"]))

            timestamp = pd.to_datetime(data["Time"], unit='s')
            utc_timestamp = timestamp.tz_localize('UTC')
            utc_plus_8_timestamp = utc_timestamp.tz_convert('Asia/Shanghai')
            formatted_times = utc_plus_8_timestamp.strftime('%Y-%m-%d')

            new_data = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Time', 'Open_time',
                                                   'Close_time'])
            new_data.index = utc_plus_8_timestamp

            return new_data
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching data for {self.symbol}: {e}")
            root.quit()
            return pd.DataFrame()

    def calculate_indicators(self):
        try:
            df = self.data
            df['MA1'] = df['Close']
            df['MA30'] = df['Close'].rolling(window=30).mean()
            df['MA72'] = df['Close'].rolling(window=72).mean()
            df['MA2'] = (df['MA30'] + df['MA72']) / 2
            df['MA3'] = df['MA2'] * 1.1
            df['MA4'] = df['MA2'] * 1.2
            df['MA5'] = df['MA2'] * 0.9
            df['MA6'] = df['MA2'] * 0.8
            return df
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating indicators for {self.symbol}: {e}")
            root.quit()
            return pd.DataFrame()

    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        # 计算短期和长期的EMA
        self.data['EMA12'] = self.data['Close'].ewm(span=short_window, adjust=False).mean()
        self.data['EMA26'] = self.data['Close'].ewm(span=long_window, adjust=False).mean()

        # 计算MACD线
        self.data['MACD'] = self.data['EMA12'] - self.data['EMA26']

        # 计算信号线
        self.data['Signal Line'] = self.data['MACD'].ewm(span=signal_window, adjust=False).mean()

        # 计算MACD柱
        self.data['MACD Histogram'] = self.data['MACD'] - self.data['Signal Line']

        return self.data


    def plot(self):
        try:
            df = self.indicators
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 5), gridspec_kw={'height_ratios': [3, 1]})

            # 绘制MA1到MA6
            ax1.plot(df['MA1'], label='current price', color='red')
            ax1.plot(df['MA2'], label='MA2', color='gray')
            ax1.plot(df['MA3'], label='MA3', color='green')
            ax1.plot(df['MA4'], label='MA4', color='yellow')
            ax1.plot(df['MA5'], label='MA5', color='green', linestyle='--')
            ax1.plot(df['MA6'], label='MA6', color='blue', linestyle='--')

            ax1.set_xticks(df.index)  # 设置x轴标签
            ax1.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better readability
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H'))  # Adjust date format as needed

            # Set interval for x-axis labels (e.g., every 2nd label)
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=10))  # Adjust interval as needed
            ax1.xaxis.set_visible(False)

            ax1.set_title(f'{self.symbol} Custom Moving Averages and Real-time Trading Signals')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Price')
            ax1.legend()
            ax1.grid()


            # 绘制MACD和信号线
            ax2.plot(df.index, df['MACD'], label='', color='blue')
            ax2.plot(df.index, df['Signal Line'], label='', color='red')

            # 绘制MACD柱状图
            colors = ['green' if val >= 0 else 'red' for val in df['MACD Histogram']]
            ax2.bar(df.index, df['MACD Histogram'], color=colors, label='MACD')

            ax2.set_xticks(df.index)
            ax2.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better readability
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H'))  # Adjust date format as needed

            # Set interval for x-axis labels (e.g., every 2nd label)
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=10))

            ax2.legend()
            # ax2.set_title('MACD and Signal Line')
            # ax2.set_xlabel('Time')
            # ax2.set_ylabel('MACD')

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Error plotting data for {self.symbol}: {e}")
            root.quit()


def run_trading_bot(symbol_list):
    for symbol in symbol_list:
        bot = TradingBot(symbol=symbol, interval='4h', limit=5000)
        bot.plot()


def submit_symbols():
    try:
        selection = select_var.get()
        if selection == "默认":
            symbols = ["SOLUSDT", "ETHUSDT", "BTCUSDT"]
        elif selection == "输入":
            custom_symbols = symbol_text.get("1.0", tk.END).strip().upper()
            custom_symbols = custom_symbols.replace('，', ',')
            symbols = [symbol.strip() + "USDT" for symbol in custom_symbols.split(",") if symbol.strip()]
        else:
            messagebox.showerror("Error", "Invalid selection.")
            return
        if not symbols:
            symbols = ["SOLUSDT", "ETHUSDT", "BTCUSDT"]
        root.destroy()
        run_trading_bot(symbols)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        root.quit()


def on_select(value):
    if value == "输入":
        symbol_text.config(state=tk.NORMAL)
    else:
        symbol_text.config(state=tk.DISABLED)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("ma图形")
    root.geometry("600x400")
    root.configure(bg="#f0f0f0")

    frame = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
    frame.pack(expand=True, fill=tk.BOTH)

    select_label = tk.Label(frame, text="币种选项 :", font=("Arial", 14), bg="#f0f0f0")
    select_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

    options = ["默认", "输入"]
    select_var = tk.StringVar(root)
    select_var.set(options[0])
    select_menu = ttk.Combobox(frame, textvariable=select_var, values=options, state="readonly", width=15,
                               font=("Arial", 12))
    select_menu.grid(row=0, column=1, pady=(0, 10))
    select_menu.bind("<<ComboboxSelected>>", lambda event: on_select(select_var.get()))

    symbol_label = tk.Label(frame, text="输入币种(间隔符,):", font=("Arial", 12), bg="#f0f0f0")
    symbol_label.grid(row=1, column=0, sticky="nw")

    symbol_text = tk.Text(frame, state=tk.DISABLED, width=40, height=10, font=("Arial", 12))
    symbol_text.grid(row=1, column=1, pady=(0, 10))

    submit_button = tk.Button(frame, text="Submit", command=submit_symbols, font=("Arial", 12), bg="#4CAF50",
                              fg="white")
    submit_button.grid(row=2, columnspan=2, pady=20)

    root.mainloop()
