from flask import render_template, jsonify, request
import logging
import concurrent.futures
from datetime import datetime
from modules.trading_analysis import KlineBot, token_trend

logger = logging.getLogger(__name__)

# 存储活跃的交易机器人实例
active_bots = {}

def init_routes(app):
    """初始化所有路由"""
    
    @app.route('/')
    def index():
        """渲染主页"""
        return render_template('layout.html')
        
    @app.route('/get_chart', methods=['POST'])
    def get_chart():
        """获取图表数据"""
        try:
            # 从表单数据中获取参数，而不是JSON
            symbol = request.form.get('symbol', 'BTC').upper().strip()
            if not symbol.endswith('USDT'):
                symbol = symbol + 'USDT'
            
            interval = request.form.get('interval', '4h')  # 默认使用4小时
            
            # 检查是否已有该交易对的机器人实例
            bot_key = f"{symbol}_{interval}"
            if bot_key not in active_bots:
                active_bots[bot_key] = KlineBot(symbol, interval)
            
            bot = active_bots[bot_key]
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
            logger.error(f"获取图表时出错: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/get_market_trends', methods=['POST'])
    def get_market_trends():
        """获取盘面趋势"""
        try:
            # 获取请求数据
            data = request.json
            symbols = data.get('symbols', [])
            interval = data.get('interval', '4h')  # 默认使用4小时
            
            # 确保所有币种都以USDT结尾
            symbols = [symbol.upper() + 'USDT' if not symbol.upper().endswith('USDT') else symbol.upper() for symbol in symbols]
            
            logger.info(f"获取多币种趋势: {symbols}, 周期: {interval}")
            
            # 定义趋势分类
            trends = {
                'above_ma4': [],    # 突破上涨黄线
                'above_ma3': [],    # 突破上涨绿线
                'between_ma2_ma3': [],  # 盘整区上行
                'between_ma5_ma2': [],  # 盘整区下行
                'below_ma5': [],    # 跌破底部绿线
                'below_ma6': []     # 跌破底部蓝线
            }
            
            # 使用线程池并行获取数据
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # 提交任务到线程池并保存 Future 对象
                future_to_symbol = {executor.submit(token_trend, symbol, interval): symbol.replace('USDT', '') for symbol in symbols}
                
                # 处理结果
                for future in concurrent.futures.as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        if result:
                            # 根据结果将币种放入相应的趋势类别
                            category = result['token_trend']
                            if category in trends:
                                trends[category].append(symbol)
                    except Exception as e:
                        logger.error(f"处理 {symbol} 趋势时出错: {e}")
            
            return jsonify({
                'success': True,
                'trends': trends
            })
        except Exception as e:
            logger.error(f"获取盘面趋势时出错: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
            
    return app 