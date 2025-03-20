from flask import Flask
import logging
from modules.routes import init_routes

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 初始化路由
    app = init_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=6969)