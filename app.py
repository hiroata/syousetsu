#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application main file for the novel generator.
Uses the application factory pattern for better modularity.
"""

import os
import logging
from flask import Flask, render_template  # render_templateをインポート
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from config import Config
from models import db, init_db
from routes import register_blueprints

# .env ファイルがあれば自動で読み込む
load_dotenv()

def create_app(config_class=Config):
    """
    アプリケーションファクトリ関数
    
    Args:
        config_class: 設定クラス
        
    Returns:
        Flask: 設定済みのFlaskアプリケーション
    """
    # ロギングの設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('novel_generator.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('novel_generator')
    
    # Flask アプリケーション初期化
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # SQLAlchemyの設定
    db.init_app(app)
    
    # セッション設定
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_FILE_THRESHOLD'] = 500  # セッションファイル数の上限
    Session(app)
    
    # 初期化処理
    with app.app_context():
        Config.init_directories()
        init_db(app)
    
    # ルートを登録
    register_blueprints(app)
    
    # エラーハンドラーの登録
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"サーバーエラー: {e}")
        return render_template('error.html', 
                              error_title='サーバーエラー',
                              error_message='申し訳ありませんが、サーバーでエラーが発生しました。後でもう一度お試しください。'), 500

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                              error_title='ページが見つかりません',
                              error_message='お探しのページは存在しないか、移動した可能性があります。'), 404
                              
    logger.info("アプリケーション初期化完了")
    
    return app

# アプリケーションインスタンスを作成（他ファイルからのインポート用）
app = create_app()

# アプリケーションを直接実行するための条件分岐
if __name__ == '__main__':
    app.run(debug=True)