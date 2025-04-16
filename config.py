#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import typing as t
from dotenv import load_dotenv

# .env ファイルがあれば自動で読み込む
load_dotenv()

class Config:
    """アプリケーション設定クラス
    
    環境変数から設定を読み込み、デフォルト値を提供します。
    また、必要なディレクトリ構造の初期化メソッドも含みます。
    """
    # 基本パス
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # アプリケーション設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-me')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # データ保存ディレクトリ
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    CHARACTER_DIR = os.path.join(DATA_DIR, 'characters')
    LOCATION_DIR = os.path.join(DATA_DIR, 'locations')
    PROMPT_DIR = os.path.join(DATA_DIR, 'prompts')
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "novel_generator.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # セッション設定
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24時間（秒）
    
    # APIキー
    XAI_API_KEY = os.getenv('XAI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_BASE = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
    
    @classmethod
    def init_directories(cls) -> None:
        """必要なディレクトリ構造を作成
        
        アプリケーションが使用するデータディレクトリが存在しない場合に作成します。
        - DATA_DIR: 基本データディレクトリ
        - CHARACTER_DIR: キャラクター情報保存ディレクトリ
        - LOCATION_DIR: 場所情報保存ディレクトリ
        - PROMPT_DIR: プロンプト保存ディレクトリ
        """
        # ディレクトリが存在しない場合は作成
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.CHARACTER_DIR, exist_ok=True)
        os.makedirs(cls.LOCATION_DIR, exist_ok=True)
        os.makedirs(cls.PROMPT_DIR, exist_ok=True)


class AIModels:
    """AIモデル設定の一元管理クラス"""
    
    # サポートされるモデル一覧
    SUPPORTED_MODELS = ['xai', 'grok-3', 'gpt-4o', 'claude-3-opus', 'deepseek-v3']
    
    # モデル表示名の定義
    MODEL_DISPLAY_NAMES = {
        'xai': 'xAI (Grok-2)',
        'grok-3': 'xAI (Grok-3)',
        'gpt-4o': 'OpenAI (GPT-4o)',
        'claude-3-opus': 'Anthropic (Claude 3 Opus)',
        'deepseek-v3': 'DeepSeek (V3-0324)'
    }
    
    # モデルのAPI識別子
    MODEL_API_IDS = {
        'xai': 'grok-2-1212',
        'grok-3': 'grok-3-1212',
        'gpt-4o': 'gpt-4o',
        'claude-3-opus': 'claude-3-opus-20240229',
        'deepseek-v3': 'deepseek-chat'  # DeepSeek APIでは'deepseek-chat'を使用
    }
    
    @classmethod
    def get_display_name(cls, model_id: str) -> str:
        """モデル識別子から表示名を取得"""
        return cls.MODEL_DISPLAY_NAMES.get(model_id, f'Unknown Model ({model_id})')
    
    @classmethod
    def get_api_id(cls, model_id: str) -> str:
        """モデル識別子からAPI識別子を取得"""
        return cls.MODEL_API_IDS.get(model_id, model_id)
    
    @classmethod
    def is_supported(cls, model_id: str) -> bool:
        """モデルがサポートされているかを確認"""
        return model_id in cls.SUPPORTED_MODELS