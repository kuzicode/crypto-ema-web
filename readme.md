# Crypto EMA Web App

这是一个加密货币技术分析工具，显示移动平均线(EMA)和MACD指标的网页应用程序。该应用采用像素风格的加密货币主题UI。

## 特点

- 网页服务器形式，而不是传统窗口应用
- 像素风加密货币主题的用户界面
- 支持通过输入加密货币代码(例如BTC)来查询
- 快速按钮选择常用加密货币
- 显示移动平均线和MACD指标
- 自定义时间间隔和数据点数量
- 适应性强的响应式设计

## 目录结构

```
crypto-ema-web/
├── app.py          # Flask主应用程序
├── requirements.txt # 依赖项列表
└── templates/      # HTML模板
    └── index.html  # 主页模板
```

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

2. 创建必要的文件:

- 将`app.py`内容复制到`app.py`文件
- 创建`templates`目录，并将`index.html`内容复制到`templates/index.html`文件
- 创建以下`requirements.txt`文件：

```
flask==2.0.1
pandas==1.3.3
matplotlib==3.4.3
requests==2.28.1
```

3. 安装依赖项:

```bash
pip install -r requirements.txt
```

4. 运行应用程序:

```bash
flask run --host=0.0.0.0 --port=6969
```

或者:

```bash
python app.py
```

5. 在浏览器中访问:

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

## 自定义

- 在`app.py`中修改`TradingBot`类以添加或修改技术指标
- 在`index.html`中编辑CSS样式以自定义UI外观

## 依赖项

- Flask: Web框架
- Pandas: 数据处理
- Matplotlib: 图表生成
- python-binance: Binance API客户端

## 注意事项

- 本应用仅用于学习和研究目的
- 不构成投资建议或推荐
- 使用Binance公共API，需要确保网络可以访问Binance