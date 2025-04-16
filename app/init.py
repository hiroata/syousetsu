cat > app/__init__.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application factory for the novel generator.
Creates and configures the Flask application.
"""

import os
import logging
import datetime
from flask import Flask
from flask_session import Session
from .models import db, init_db
from config import Config

def create_app(config_class=Config):
    """
    アプリケーションファクトリ関数
    
    Args:
        config_class: 設定クラス
        
    Returns:
        Flask: 設定済みのFlaskアプリケーション
    """
    # Flask アプリケーション初期化
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ロギングの設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('novel_generator.log'),
            logging.StreamHandler()
        ]
    )
    
    # SQLAlchemyの設定
    db.init_app(app)
    
    # セッション設定
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)
    app.config['SESSION_FILE_THRESHOLD'] = 500  # セッションファイル数の上限
    Session(app)
    
    # 初期化処理
    with app.app_context():
        Config.init_directories()
        init_db(app)
    
    # ルートを登録
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # エラーハンドラーの登録
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """
    エラーハンドラーを登録する
    
    Args:
        app: Flaskアプリケーション
    """
    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"サーバーエラー: {e}")
        return render_template('error.html', 
                              error_title='サーバーエラー',
                              error_message='申し訳ありませんが、サーバーでエラーが発生しました。後でもう一度お試しください。'), 500

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                              error_title='ページが見つかりません',
                              error_message='お探しのページは存在しないか、移動した可能性があります。'), 404
EOF