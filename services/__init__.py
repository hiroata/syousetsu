#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Style service for the novel generator application.
Handles text style conversion and style-related functionality.
"""

import logging
from typing import Dict, Any, Optional
from .novel_templates import get_style_by_id

# ロギングの設定
logger = logging.getLogger('novel_generator')

def create_style_conversion_prompt(text: str, style_id: str) -> str:
    """
    文体変換のためのプロンプトを作成する
    
    Args:
        text: 変換対象のテキスト
        style_id: 目標とする文体スタイルのID
        
    Returns:
        str: 文体変換プロンプト
    """
    # 文体の取得
    style = get_style_by_id(style_id)
    if not style:
        logger.error(f"無効な文体ID: {style_id}")
        return ""
    
    # プロンプト作成
    prompt = f"""
あなたは文体変換の専門家です。以下のテキストを「{style['name']}」の文体に変換してください。

### 変換対象テキスト:
{text}

### 目標とする文体の特徴:
{style['description']}
"""
    
    # サンプル文があれば追加
    if 'sample' in style:
        prompt += f"\n### 文体サンプル:\n{style['sample']}\n"
    
    # 指示を追加
    prompt += """
### 指示:
- 内容は保持しつつ、文体のみを変換してください
- 段落構造や会話の構造は維持してください
- 官能的な表現や描写のニュアンスは保持してください
- 原文と同程度の長さを維持してください
"""
    
    return prompt

def get_style_characteristics(style_id: str) -> Dict[str, Any]:
    """
    指定された文体の特徴を取得する
    
    Args:
        style_id: 文体スタイルのID
        
    Returns:
        Dict[str, Any]: 文体の特徴情報
    """
    style = get_style_by_id(style_id)
    if not style:
        logger.error(f"無効な文体ID: {style_id}")
        return {}
    
    # 基本情報を返す
    return {
        'name': style.get('name', '不明'),
        'description': style.get('description', ''),
        'characteristics': style.get('characteristics', []),
        'has_sample': 'sample' in style
    }

def generate_style_examples(style_id: str, scene_type: Optional[str] = None) -> str:
    """
    指定された文体のサンプル生成用プロンプトを作成する
    
    Args:
        style_id: 文体スタイルのID
        scene_type: シーンタイプ（オプション）
        
    Returns:
        str: サンプル生成用プロンプト
    """
    style = get_style_by_id(style_id)
    if not style:
        logger.error(f"無効な文体ID: {style_id}")
        return ""
    
    # プロンプト作成
    prompt = f"あなたは官能小説作家です。「{style['name']}」の文体で以下のようなサンプル文を生成してください。\n\n"
    prompt += f"### 文体の特徴:\n{style['description']}\n\n"
    
    # サンプル文があれば追加
    if 'sample' in style:
        prompt += f"### 文体サンプル:\n{style['sample']}\n\n"
    
    # シーンタイプに応じた指示
    if scene_type:
        prompt += f"### シーンタイプ:\n{scene_type} シーンを書いてください。\n\n"
    
    # 生成指示
    prompt += """
### 指示:
- 300〜400文字程度のサンプルを生成してください
- 指定された文体の特徴を明確に表現してください
- 官能的な表現を適切に含めてください
- 段落構造や会話を適切に配置してください
"""
    
    return prompt

def apply_style_elements(base_text: str, style_elements: Dict[str, str]) -> str:
    """
    基本テキストに文体要素を適用するプロンプトを作成する
    
    Args:
        base_text: 基本テキスト
        style_elements: 適用する文体要素（キーと値のペア）
        
    Returns:
        str: 文体要素適用プロンプト
    """
    prompt = "あなたは文体編集の専門家です。以下のテキストを指定された文体要素に基づいて編集してください。\n\n"
    prompt += f"### 編集対象テキスト:\n{base_text}\n\n"
    
    # 文体要素を追加
    prompt += "### 適用する文体要素:\n"
    for element_name, element_desc in style_elements.items():
        prompt += f"- {element_name}: {element_desc}\n"
    prompt += "\n"
    
    # 指示を追加
    prompt += """
### 指示:
- 指定された文体要素を適用してテキストを編集してください
- テキストの内容や構造は維持してください
- 段落や会話の構成は保持してください
- 編集後のテキストは原文と同程度の長さにしてください
"""
    
    return prompt