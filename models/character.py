#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Character model for the novel generator application.
"""

import json
import datetime
import uuid
from typing import Dict, List, Optional, Any, Union

class Character:
    """キャラクターモデルクラス"""
    
    @staticmethod
    def create(character_data: Dict[str, Any]) -> Dict[str, Any]:
        """新しいキャラクターを作成する"""
        character = {
            'id': str(uuid.uuid4()),  # 一意のID生成
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            **character_data
        }
        # 実際はデータベースに保存するが、ここでは単にデータを返す
        return character
    
    @staticmethod
    def update(character_id: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """キャラクター情報を更新する"""
        # 実際はデータベースから取得して更新するが、ここではダミーデータを返す
        character = {
            'id': character_id,
            'updated_at': datetime.datetime.now(),
            **character_data
        }
        return character
    
    @staticmethod
    def find_by_id(character_id: str) -> Optional[Dict[str, Any]]:
        """IDでキャラクターを検索する"""
        # 実際はデータベースから検索するが、ここではダミーデータを返す
        return {
            'id': character_id,
            'name': 'テスト太郎',
            'gender': 'male',
            'age': '30',
            'occupation': '会社員',
            'appearance': '背が高く、精悍な顔立ち',
            'personality': '穏やかだが芯が強い',
            'speech_pattern': '丁寧な口調',
            'kinks': '優しい、背中フェチ',
            'tags': 'サンプル, テスト',
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now()
        }
    
    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """すべてのキャラクターを取得する"""
        # 実際はデータベースから取得するが、ここではダミーデータを返す
        return [
            {
                'id': '1',
                'name': 'テスト太郎',
                'gender': 'male',
                'age': '30',
                'occupation': '会社員',
                'appearance': '背が高く、精悍な顔立ち',
                'personality': '穏やかだが芯が強い',
                'kinks': '優しい、背中フェチ',
                'tags': 'サンプル, テスト'
            },
            {
                'id': '2',
                'name': 'テスト花子',
                'gender': 'female',
                'age': '28',
                'occupation': 'デザイナー',
                'appearance': 'スレンダーで洗練された雰囲気',
                'personality': '明るく社交的',
                'kinks': '甘え上手、首筋弱い',
                'tags': 'サンプル, テスト'
            }
        ]
    
    @staticmethod
    def delete(character_id: str) -> bool:
        """キャラクターを削除する"""
        # 実際はデータベースから削除するが、ここでは常に成功を返す
        return True