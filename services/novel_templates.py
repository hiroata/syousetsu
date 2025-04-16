#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Template service for the novel generator application.
Handles loading and fetching templates, writing styles, and story structures.
"""

import os
import json
import random
import logging
from typing import Dict, List, Any, Optional, Union

# ロギングの設定
logger = logging.getLogger('novel_generator')

def load_templates() -> List[Dict[str, Any]]:
    """
    テンプレート一覧を読み込む
    
    Returns:
        List[Dict[str, Any]]: テンプレートのリスト
    """
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'templates.json')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"テンプレート読み込みエラー: {e}")
        return []

def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """
    IDを指定してテンプレートを取得
    
    Args:
        template_id: テンプレートのID
        
    Returns:
        Optional[Dict[str, Any]]: テンプレート情報
    """
    templates = load_templates()
    for template in templates:
        if template.get('id') == template_id:
            return template
    return None

def load_writing_styles() -> List[Dict[str, Any]]:
    """
    文体サンプル一覧を読み込む
    
    Returns:
        List[Dict[str, Any]]: 文体サンプルのリスト
    """
    styles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'writing_styles.json')
    try:
        with open(styles_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"文体サンプル読み込みエラー: {e}")
        return []

def get_style_by_id(style_id: str) -> Optional[Dict[str, Any]]:
    """
    IDを指定して文体サンプルを取得
    
    Args:
        style_id: 文体サンプルのID
        
    Returns:
        Optional[Dict[str, Any]]: 文体サンプル情報
    """
    styles = load_writing_styles()
    for style in styles:
        if style.get('id') == style_id:
            return style
    return None

def get_random_murakami_style() -> Dict[str, Any]:
    """
    ランダムな村上龍風文体を取得
    
    Returns:
        Dict[str, Any]: 村上龍風文体の情報
    """
    styles = load_writing_styles()
    # murakami_ryu で始まるIDのスタイルだけをフィルタリング
    murakami_styles = [style for style in styles if style.get('id', '').startswith('murakami_ryu')]
    if murakami_styles:
        return random.choice(murakami_styles)
    # 見つからない場合はデフォルト返す
    return {"id": "murakami_ryu_1", "name": "村上龍風", "description": "都市の闇と若者文化の融合。"}

def load_story_structures() -> List[Dict[str, Any]]:
    """
    ストーリー構造テンプレート一覧を読み込む
    
    Returns:
        List[Dict[str, Any]]: ストーリー構造テンプレートのリスト
    """
    structures_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'story_structures.json')
    try:
        with open(structures_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"ストーリー構造読み込みエラー: {e}")
        return []

def get_structure_by_id(structure_id: str) -> Optional[Dict[str, Any]]:
    """
    IDを指定してストーリー構造テンプレートを取得
    
    Args:
        structure_id: ストーリー構造テンプレートのID
        
    Returns:
        Optional[Dict[str, Any]]: ストーリー構造テンプレート情報
    """
    structures = load_story_structures()
    for structure in structures:
        if structure.get('id') == structure_id:
            return structure
    return None