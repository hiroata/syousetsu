#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Location model for the novel generator application.
"""

import uuid
import datetime
from typing import Dict, List, Optional, Any

class Location:
    """場所モデルクラス"""
    
    @staticmethod
    def create(location_data: Dict[str, Any]) -> Dict[str, Any]:
        """新しい場所を作成する"""
        location = {
            'id': str(uuid.uuid4()),  # 一意のID生成
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            **location_data
        }
        # 実際はデータベースに保存するが、ここでは単にデータを返す
        return location
    
    @staticmethod
    def update(location_id: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """場所情報を更新する"""
        # 実際はデータベースから取得して更新するが、ここではダミーデータを返す
        location = {
            'id': location_id,
            'updated_at': datetime.datetime.now(),
            **location_data
        }
        return location
    
    @staticmethod
    def find_by_id(location_id: str) -> Optional[Dict[str, Any]]:
        """IDで場所を検索する"""
        # 実際はデータベースから検索するが、ここではダミーデータを返す
        return {
            'id': location_id,
            'name': 'サンプルホテル',
            'category': 'ホテル',
            'description': '都会の高級ホテル。最上階の部屋から街の夜景が一望できる。',
            'atmosphere': '洗練された雰囲気で、モダンな内装。',
            'features': '広いキングサイズベッド、大きな窓、充実したバスルーム。',
            'tags': '高級, 夜景, 都会',
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now()
        }
    
    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """すべての場所を取得する"""
        # 実際はデータベースから取得するが、ここではダミーデータを返す
        return [
            {
                'id': '1',
                'name': 'サンプルホテル',
                'category': 'ホテル',
                'description': '都会の高級ホテル。最上階の部屋から街の夜景が一望できる。',
                'tags': '高級, 夜景, 都会'
            },
            {
                'id': '2',
                'name': '隠れ家カフェ',
                'category': 'カフェ',
                'description': '人通りの少ない路地裏にある小さなカフェ。落ち着いた雰囲気が特徴。',
                'tags': '隠れ家, 静か, 落ち着き'
            }
        ]
    
    @staticmethod
    def delete(location_id: str) -> bool:
        """場所を削除する"""
        # 実際はデータベースから削除するが、ここでは常に成功を返す
        return True