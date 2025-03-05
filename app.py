from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import base64
import io
import os
import logging
import requests
import json
import time
from datetime import datetime as dt

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# REST API: 币安 API K-line数据 
def get_klines(symbol, interval, limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        app.logger.error(f"Failed to retrieve K-line data: {response.text}")
        return []

# 辅助函数 - 解析币安K线数据的格式
def parser_klines(kline):
    return {
        "Open_time": kline[0],
        "Open": kline[1],
        "High": kline[2],
        "Low": kline[3],
        "Close": kline[4],
        "Volume": kline[5],
        "Close_time": kline[6],
        "Quote_asset_volume": kline[7],
        "Number_of_trades": kline[8],
        "Taker_buy_base_asset_volume": kline[9],
        "Taker_buy_quote_asset_volume": kline[10],
        "Ignore": kline[11]
    }

# 时间格式化函数
def get_alltime(time):
    try:
        formatted_time = datetime.datetime.fromtimestamp(time / 1000)
        return formatted_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        app.logger.error(f"时间格式化错误: {e}")
        return str(time)

class TradingBot:
    def __init__(self, symbol, interval="4h"):
        self.symbol = symbol
        self.interval = interval
        self.limit = 5000  # 固定为5000，以获取更多的数据点
        self.data = self.fetch_data()
        if not self.data.empty:
            self.calculate_macd()
            self.indicators = self.calculate_indicators()
        else:
            self.indicators = pd.DataFrame()

    def fetch_data(self):
        try:
            app.logger.info(f"正在获取 {self.symbol} 的数据...")
            
            # Get Data
            klines = get_klines(self.symbol, self.interval, self.limit)
            
            if not klines:
                app.logger.error(f"获取 {self.symbol} 的K线数据失败")
                return pd.DataFrame()
                
            data = {
                "Open": [], "High": [], "Low": [], "Close": [],
                "Time": [], "Volume": [], "Open_time": [], "Close_time": []
            }

            for kline in klines:
                data["Open_time"].append(get_alltime(kline[0]))
                data["Close_time"].append(get_alltime(kline[6]))
                data["Open"].append(float(kline[1]))
                data["High"].append(float(kline[2]))
                data["Low"].append(float(kline[3]))
                data["Close"].append(float(kline[4]))
                data["Volume"].append(float(kline[5]))
                data["Time"].append(float(kline[0]) / 1000)

            # 转换时间戳到pandas datetime
            timestamp = pd.to_datetime(data["Time"], unit='s')
            
            # 创建DataFrame并设置索引
            new_data = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Time', 'Open_time', 'Close_time'])
            
            # 尝试将时间戳设置为索引，同时处理时区
            try:
                utc_timestamp = timestamp.tz_localize('UTC')
                utc_plus_8_timestamp = utc_timestamp.tz_convert('Asia/Shanghai')
                new_data.index = utc_plus_8_timestamp
            except:
                # 如果时区转换失败，使用原始时间戳作为索引
                new_data.index = timestamp

            return new_data
        except Exception as e:
            app.logger.error(f"Get {self.symbol} data error: {e}")
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
            app.logger.error(f"计算 {self.symbol} 指标时出错: {e}")
            return pd.DataFrame()

    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        try:
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
        except Exception as e:
            app.logger.error(f"计算 {self.symbol} MACD时出错: {e}")
            return self.data
            
    def generate_market_analysis(self):
        """生成市场分析和买入建议"""
        try:
            if self.indicators.empty:
                return None
                
            df = self.indicators
            # 获取最近的数据点
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 市场分析
            analysis = {
                "latest_close": latest["Close"],
                "latest_time": latest.name.strftime('%Y-%m-%d %H:%M') if hasattr(latest.name, 'strftime') else "最新",
                "ma30": latest["MA30"],
                "ma72": latest["MA72"],
                "ma2": latest["MA2"],
                "macd": latest["MACD"],
                "signal": latest["Signal Line"],
                "histogram": latest["MACD Histogram"],
                "prev_histogram": prev["MACD Histogram"],
                "trend": "",
                "signal_type": "",
                "risk_level": "",
                "suggestion": ""
            }
            
            # 趋势判断
            if latest["Close"] > latest["MA2"]:
                if latest["Close"] > latest["MA3"]:
                    analysis["trend"] = "强势上升"
                else:
                    analysis["trend"] = "上升"
            elif latest["Close"] < latest["MA2"]:
                if latest["Close"] < latest["MA5"]:
                    analysis["trend"] = "强势下降"
                else:
                    analysis["trend"] = "下降"
            else:
                analysis["trend"] = "横盘整理"
            
            # MACD信号类型
            if latest["MACD"] > latest["Signal Line"]:
                if latest["MACD Histogram"] > prev["MACD Histogram"]:
                    analysis["signal_type"] = "金叉后动能增强"
                else:
                    analysis["signal_type"] = "金叉"
            else:
                if latest["MACD Histogram"] < prev["MACD Histogram"]:
                    analysis["signal_type"] = "死叉后动能增强"
                else:
                    analysis["signal_type"] = "死叉"
            
            # 风险水平
            price_volatility = (latest["High"] - latest["Low"]) / latest["Close"] * 100
            if price_volatility > 5:
                analysis["risk_level"] = "高"
            elif price_volatility > 2:
                analysis["risk_level"] = "中"
            else:
                analysis["risk_level"] = "低"
            
            # 买入建议
            if analysis["trend"] == "强势上升" and analysis["signal_type"] == "金叉后动能增强":
                analysis["suggestion"] = "强烈买入"
            elif analysis["trend"] == "上升" and analysis["signal_type"] == "金叉":
                analysis["suggestion"] = "买入"
            elif analysis["trend"] == "下降" and analysis["signal_type"] == "死叉":
                analysis["suggestion"] = "卖出"
            elif analysis["trend"] == "强势下降" and analysis["signal_type"] == "死叉后动能增强":
                analysis["suggestion"] = "强烈卖出"
            elif analysis["trend"] == "横盘整理":
                analysis["suggestion"] = "观望"
            elif analysis["trend"] == "上升" and analysis["signal_type"] == "死叉":
                analysis["suggestion"] = "减仓"
            elif analysis["trend"] == "下降" and analysis["signal_type"] == "金叉":
                analysis["suggestion"] = "谨慎买入"
            else:
                analysis["suggestion"] = "观望"
                
            # 添加支撑和阻力位
            last_50 = df.iloc[-50:]
            support = last_50["Low"].min()
            resistance = last_50["High"].max()
            
            analysis["support"] = support
            analysis["resistance"] = resistance
            
            return analysis
            
        except Exception as e:
            app.logger.error(f"生成市场分析时出错: {e}")
            return None

    def generate_plot(self):
        try:
            if self.indicators.empty:
                return None, f"No data available for {self.symbol}. Please check if this symbol exists on OKX."
                
            df = self.indicators
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), gridspec_kw={'height_ratios': [3, 1]})
            plt.style.use('dark_background')  # 使用暗色主题，更符合加密货币风格

            # 绘制MA1到MA6
            ax1.plot(df['MA1'], label='Current Price', color='#00FFFF', linewidth=2)  # 青色
            ax1.plot(df['MA2'], label='MA2', color='#808080')
            ax1.plot(df['MA3'], label='MA3', color='#32CD32')
            ax1.plot(df['MA4'], label='MA4', color='#FFFF00')
            ax1.plot(df['MA5'], label='MA5', color='#32CD32', linestyle='--')
            ax1.plot(df['MA6'], label='MA6', color='#4169E1', linestyle='--')

            # 设置日期格式和刻度
            # 调整为每50个点取一个刻度，避免过多刻度导致的显示问题
            ax1.set_xticks(df.index[::50])  
            ax1.tick_params(axis='x', rotation=45)
            ax1.tick_params(colors='#00FF00')  # 绿色坐标轴文字
            
            # 尝试使用日期格式化器，如果索引是日期时间类型
            try:
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            except:
                pass
                
            ax1.xaxis.set_visible(False)

            ax1.set_title(f'{self.symbol} Moving Averages', color='#00FF00', fontsize=16)
            ax1.set_ylabel('Price', color='#00FF00')
            ax1.legend()
            
            # 像素风格化：网格和背景
            ax1.grid(True, linestyle='--', alpha=0.3, color='#4B0082')
            ax1.set_facecolor('#000033')  # 深蓝背景
            
            # 添加当前价格标注
            current_price = df['Close'].iloc[-1]
            ax1.text(df.index[-1], current_price, f"  {current_price:.2f}", 
                    color='#00FFFF', fontweight='bold', verticalalignment='center')
            
            # 绘制MACD和信号线
            ax2.plot(df.index, df['MACD'], label='MACD', color='#00FFFF', linewidth=1.5)
            ax2.plot(df.index, df['Signal Line'], label='Signal', color='#FF00FF', linewidth=1.5)

            # 绘制MACD柱状图
            colors = ['#00FF00' if val >= 0 else '#FF0000' for val in df['MACD Histogram']]
            ax2.bar(df.index, df['MACD Histogram'], color=colors, width=0.7, alpha=0.7)

            # 设置日期格式和刻度
            ax2.set_xticks(df.index[::50])
            ax2.tick_params(axis='x', rotation=45, colors='#00FF00')
            
            # 尝试使用日期格式化器，如果索引是日期时间类型
            try:
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            except:
                pass
                
            ax2.set_xlabel('Date', color='#00FF00')
            ax2.set_ylabel('MACD', color='#00FF00')
            ax2.legend(facecolor='#000033', edgecolor='#32CD32')
            ax2.grid(True, linestyle='--', alpha=0.3, color='#4B0082')
            ax2.set_facecolor('#000033')

            fig.patch.set_facecolor('#000033')
            plt.tight_layout()
            
            # 转换为base64编码的图像
            buf = io.BytesIO()
            plt.savefig(buf, format='png', facecolor='#000033', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            
            return img_str, None
        except Exception as e:
            app.logger.error(f"生成{self.symbol}图表时出错: {e}")
            return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_chart', methods=['POST'])
def get_chart():
    try:
        symbol = request.form.get('symbol', 'BTC').upper().strip()
        if not symbol.endswith('USDT'):
            symbol = symbol + 'USDT'
        
        interval = request.form.get('interval', '4h')
        
        bot = TradingBot(symbol=symbol, interval=interval)
        img_str, error = bot.generate_plot()
        
        if error:
            return jsonify({'success': False, 'error': error})
            
        # 获取市场分析
        market_analysis = bot.generate_market_analysis()
        
        # 获取当前最新价格
        market_info = {
            "price": f"{bot.indicators['Close'].iloc[-1]:.2f} USDT"
        }
        
        return jsonify({
            'success': True, 
            'image': img_str,
            'market_info': market_info,
            'analysis': market_analysis
        })
    except Exception as e:
        app.logger.error(f"处理请求时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6969)