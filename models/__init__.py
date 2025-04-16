"""
モデルパッケージの初期化
データベース接続とモデルの設定
"""

# 擬似データベース接続（実際のデータベースを使用しない場合）
class DummyDB:
    def __init__(self):
        self.data = {}
    
    def init_app(self, app):
        app.config.setdefault('DB_TYPE', 'dummy')
        print("擬似DBを初期化しました")

# データベースオブジェクト
db = DummyDB()

# データベース初期化関数
def init_db(app):
    """アプリケーションインスタンスでデータベースを初期化する"""
    db.init_app(app)
    
    # 初期データなどの設定があればここに記述
    return True

# 必要なモデルをインポート
from .character import Character
from .location import Location