# Crypto EMA Web App

一个加密货币技术分析工具


## Installation

1. Create project directory and set up virtual environment:

```bash
mkdir -p crypto-ema-web/templates
cd crypto-ema-web
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Access in browser:

```
http://localhost:6969
```

## Dependencies

- Flask: Web framework
- Pandas: Data processing
- Matplotlib: Chart generation
- Request: Access Binance API