# Crypto EMA Web App

一个加密货币技术分析工具，显示移动平均线(EMA)和MACD指标。


## 安装步骤

1. 创建项目目录并设置虚拟环境:

```bash
mkdir -p crypto-ema-web/templates
cd crypto-ema-web
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或者在Windows上:
# .venv\Scripts\activate
```

2. 安装依赖项:

```bash
pip install -r requirements.txt
```

3. 运行应用程序:

```bash
flask run --host=0.0.0.0 --port=6969
```

或者:

```bash
python app.py
```

4. 在浏览器中访问:

```
http://localhost:6969
```

## 使用方法

1. 访问网页应用
2. 使用快速按钮选择常见加密货币或在输入框中输入代码(如BTC、ETH、SOL等)
3. 选择时间间隔(15分钟、1小时、4小时、1天、1周)
4. 选择要显示的数据点数量
5. 点击"GENERATE CHART"按钮生成图表
6. 图表将显示选定加密货币的移动平均线和MACD指标


## 依赖项

- Flask: Web框架
- Pandas: 数据处理
- Matplotlib: 图表生成
- Request: 访问 Binance API

## 注意事项

- 本应用仅用于学习和研究目的
- 不构成投资建议或推荐
- 使用Binance公共API，需要确保网络可以访问Binance