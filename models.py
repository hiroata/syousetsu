# models.py
import os
import json
import datetime
from typing import List, Dict, Any, Optional
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

# キャラクターモデル
class Character(db.Model):
    """キャラクター情報を表すデータベースモデル"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), default='female')
    age = db.Column(db.Integer, default=25)
    occupation = db.Column(db.String(100))
    appearance = db.Column(db.Text)
    personality = db.Column(db.Text)
    background = db.Column(db.Text)
    kinks = db.Column(db.Text)  # カンマ区切りの性癖
    tags = db.Column(db.String(200))  # カンマ区切りのタグ
    speech_pattern = db.Column(db.Text)  # 話し方の特徴
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """モデルを辞書形式に変換
        
        Returns:
            キャラクター情報の辞書
        """
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'occupation': self.occupation,
            'appearance': self.appearance,
            'personality': self.personality,
            'background': self.background,
            'kinks': self.kinks,
            'tags': self.tags,
            'speech_pattern': self.speech_pattern,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def save_to_json(self) -> str:
        """キャラクター情報をJSONファイルに保存
        
        Returns:
            保存されたファイルのパス
        """
        try:
            char_dict = self.to_dict()
            filename = f"{self.id}_{self.name.replace(' ', '_')}.json"
            filepath = os.path.join(Config.CHARACTER_DIR, filename)
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(char_dict, f, ensure_ascii=False, indent=2)
                
            return filepath
        except Exception as e:
            raise IOError(f"キャラクター情報の保存に失敗しました: {e}")
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'Character':
        """JSONファイルからキャラクター情報を読み込み
        
        Args:
            filepath: JSONファイルのパス
            
        Returns:
            読み込まれたCharacterインスタンス
            
        Raises:
            IOError: ファイルの読み込みに失敗した場合
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # DBに保存されていない場合は新規作成
            character = cls.query.get(data.get('id'))
            if not character:
                character = cls()
                
            # 各フィールドを設定
            for key, value in data.items():
                if key not in ['created_at', 'updated_at'] and hasattr(character, key):
                    setattr(character, key, value)
                    
            return character
        except Exception as e:
            raise IOError(f"キャラクター情報の読み込みに失敗しました: {e}")
    
    @classmethod
    def get_all_json(cls) -> List['Character']:
        """すべてのJSONファイルからキャラクター情報を読み込み
        
        Returns:
            Characterオブジェクトのリスト
        """
        characters = []
        
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(Config.CHARACTER_DIR, exist_ok=True)
            
            for filename in os.listdir(Config.CHARACTER_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(Config.CHARACTER_DIR, filename)
                    try:
                        character = cls.load_from_json(filepath)
                        characters.append(character)
                    except Exception as e:
                        print(f"Error loading character {filename}: {e}")
        except Exception as e:
            print(f"Error accessing character directory: {e}")
        
        return characters
    
    def get_description(self) -> str:
        """プロンプト用のキャラクター説明を生成
        
        Returns:
            整形されたキャラクター説明
        """
        description = f"{self.name}（{self.age}歳）"
        
        if self.occupation:
            description += f"は{self.occupation}"
        
        description += "。"
        
        if self.appearance:
            description += f" {self.appearance}"
        
        if self.personality:
            description += f" 性格は{self.personality}。"
        
        if self.background:
            description += f" {self.background}"
        
        if self.kinks:
            description = f"【性癖: {self.kinks}】\n" + description
            
        if self.speech_pattern:
            description += f"\n【話し方: {self.speech_pattern}】"
            
        return description

# 場所モデル
class Location(db.Model):
    """場所情報を表すデータベースモデル"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # ホテル、カフェ、公園など
    description = db.Column(db.Text)
    atmosphere = db.Column(db.Text)  # 場所の雰囲気
    features = db.Column(db.Text)  # 特徴的な要素
    tags = db.Column(db.String(200))  # カンマ区切りのタグ
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """モデルを辞書形式に変換
        
        Returns:
            場所情報の辞書
        """
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'atmosphere': self.atmosphere,
            'features': self.features,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def save_to_json(self) -> str:
        """場所情報をJSONファイルに保存
        
        Returns:
            保存されたファイルのパス
        """
        try:
            location_dict = self.to_dict()
            filename = f"{self.id}_{self.name.replace(' ', '_')}.json"
            filepath = os.path.join(Config.LOCATION_DIR, filename)
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(location_dict, f, ensure_ascii=False, indent=2)
                
            return filepath
        except Exception as e:
            raise IOError(f"場所情報の保存に失敗しました: {e}")
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'Location':
        """JSONファイルから場所情報を読み込み
        
        Args:
            filepath: JSONファイルのパス
            
        Returns:
            読み込まれたLocationインスタンス
            
        Raises:
            IOError: ファイルの読み込みに失敗した場合
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # DBに保存されていない場合は新規作成
            location = cls.query.get(data.get('id'))
            if not location:
                location = cls()
                
            # 各フィールドを設定
            for key, value in data.items():
                if key not in ['created_at', 'updated_at'] and hasattr(location, key):
                    setattr(location, key, value)
                    
            return location
        except Exception as e:
            raise IOError(f"場所情報の読み込みに失敗しました: {e}")
    
    @classmethod
    def get_all_json(cls) -> List['Location']:
        """すべてのJSONファイルから場所情報を読み込み
        
        Returns:
            Locationオブジェクトのリスト
        """
        locations = []
        
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(Config.LOCATION_DIR, exist_ok=True)
            
            for filename in os.listdir(Config.LOCATION_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(Config.LOCATION_DIR, filename)
                    try:
                        location = cls.load_from_json(filepath)
                        locations.append(location)
                    except Exception as e:
                        print(f"Error loading location {filename}: {e}")
        except Exception as e:
            print(f"Error accessing location directory: {e}")
        
        return locations
    
    def get_description(self) -> str:
        """プロンプト用の場所説明を生成
        
        Returns:
            整形された場所説明
        """
        description = f"{self.name}"
        
        if self.category:
            description += f"は{self.category}。"
        else:
            description += "。"
        
        if self.description:
            description += f" {self.description}"
        
        if self.atmosphere:
            description += f" {self.atmosphere}の雰囲気。"
        
        if self.features:
            description += f" {self.features}。"
            
        return description

# DBテーブル初期化
def init_db(app) -> None:
    """データベーステーブルの初期化
    
    Args:
        app: Flaskアプリケーションインスタンス
    """
    with app.app_context():
        db.create_all()