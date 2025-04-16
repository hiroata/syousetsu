#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Story service for the novel generator application.
Handles story generation, structure, and plotting functions.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from .novel_templates import load_story_structures, get_structure_by_id

# ロギングの設定
logger = logging.getLogger('novel_generator')

def get_story_structure_prompt(structure_id: str) -> str:
    """
    指定されたストーリー構造のプロンプトを生成する
    
    Args:
        structure_id: ストーリー構造ID
        
    Returns:
        str: ストーリー構造のプロンプト
    """
    structure = get_structure_by_id(structure_id)
    if not structure:
        return ""
    
    prompt = f"## ストーリー構造: {structure.get('name', '')}\n\n"
    prompt += structure.get('description', '') + "\n\n"
    
    # 構造に基づいたガイドを追加
    if 'guide' in structure:
        prompt += "### ストーリー展開ガイド:\n"
        prompt += structure['guide'] + "\n\n"
    
    # 構造に基づいたマイルストーンを追加
    if 'milestones' in structure and isinstance(structure['milestones'], list):
        prompt += "### 主要なマイルストーン:\n"
        for i, milestone in enumerate(structure['milestones']):
            prompt += f"{i+1}. {milestone}\n"
    
    return prompt

def generate_synopsis_prompt(
    main_prompt: str,
    writing_style: str,
    characters: List[Dict[str, str]],
    settings: str,
    structure_id: Optional[str] = None,
    explicit_level: str = "70",
    detail_level: str = "80",
    psychological_level: str = "60"
) -> str:
    """
    あらすじ生成用のプロンプトを作成する
    
    Args:
        main_prompt: メインプロンプト
        writing_style: 文体
        characters: 登場人物情報のリスト
        settings: 基本設定
        structure_id: ストーリー構造ID（オプション）
        explicit_level: 淫語レベル（0-100）
        detail_level: 描写詳細度（0-100）
        psychological_level: 心理描写の深さ（0-100）
        
    Returns:
        str: あらすじ生成用プロンプト
    """
    prompt = "あなたは官能小説作家です。以下の設定に基づいて、官能小説の3話分のあらすじを作成してください。\n\n"
    prompt += f"### メインプロンプト:\n{main_prompt}\n\n"
    
    # 文体指定
    prompt += f"### 文体:\n{writing_style}の文体で書いてください。\n\n"
    
    # 登場人物
    if characters:
        prompt += "### 登場人物:\n"
        for c in characters:
            prompt += f"{c['name']}: {c['description']}\n"
        prompt += "\n"
    
    # 基本設定
    if settings:
        prompt += f"### 絶対守るべき設定:\n{settings}\n\n"
    
    # 表現レベル設定
    prompt += f"### 表現レベル設定:\n"
    prompt += f"- 淫語レベル: {explicit_level}% (値が高いほど直接的で卑猥な表現を使用)\n"
    prompt += f"- 描写詳細度: {detail_level}% (値が高いほど細部までの生々しい描写)\n"
    prompt += f"- 心理描写の深さ: {psychological_level}% (値が高いほど登場人物の内面を掘り下げる)\n\n"
    
    # ストーリー構造
    if structure_id:
        structure_prompt = get_story_structure_prompt(structure_id)
        if structure_prompt:
            prompt += f"### ストーリー構造:\n{structure_prompt}\n\n"
    
    # 生成指示
    prompt += (
        "### 指示:\n"
        "- 3話分のあらすじを作成してください\n"
        "- 各話は明確に「第1話:」「第2話:」「第3話:」などのラベルを付けてください\n"
        "- 各話は200〜300文字程度で簡潔に要約してください\n"
        "- 1話目は導入、2話目は展開、3話目はクライマックスになるよう構成してください\n"
        "- 官能描写のあるシーンは「〜〜という情事があった」など簡潔に示してください\n"
    )
    
    return prompt

def generate_episode_prompt(
    episode_num: int,
    main_prompt: str,
    synopsis: str,
    writing_style: Dict[str, str],
    characters: List[Dict[str, str]],
    settings: str,
    previous_summary: Optional[str] = None,
    direction_request: Optional[str] = None,
    direction_tags: Optional[str] = None,
    explicit_level: str = "70",
    detail_level: str = "80",
    psychological_level: str = "60"
) -> str:
    """
    エピソード執筆用のプロンプトを作成する
    
    Args:
        episode_num: エピソード番号
        main_prompt: メインプロンプト
        synopsis: あらすじ
        writing_style: 文体情報
        characters: 登場人物情報のリスト
        settings: 基本設定
        previous_summary: 前話の要約（オプション）
        direction_request: 方向性リクエスト（オプション）
        direction_tags: 方向性タグ（オプション）
        explicit_level: 淫語レベル（0-100）
        detail_level: 描写詳細度（0-100）
        psychological_level: 心理描写の深さ（0-100）
        
    Returns:
        str: エピソード執筆用プロンプト
    """
    prompt = f"あなたは官能小説作家です。以下の設定と情報に基づいて、官能小説の第{episode_num}話を執筆してください。\n\n"
    prompt += f"### メインプロンプト:\n{main_prompt}\n\n"
    
    # あらすじ
    if synopsis:
        prompt += f"### 第{episode_num}話のあらすじ:\n{synopsis}\n\n"
    
    # 方向性タグ
    if direction_tags:
        prompt += f"### 次話の方向性タグ:\n{direction_tags}\n\n"
    
    # 方向性リクエスト
    if direction_request:
        prompt += f"### 方向性リクエスト:\n{direction_request}\n\n"
    
    # 前話の要約
    if previous_summary:
        prompt += f"### 前話の内容要約:\n{previous_summary}\n\n"
    
    # 文体指定
    prompt += f"### 文体:\n{writing_style['name']}の文体で書いてください。{writing_style.get('description', '')}\n"
    if 'sample' in writing_style:
        prompt += f"サンプル文: {writing_style['sample']}\n\n"
    
    # 登場人物
    if characters:
        prompt += "### 登場人物:\n"
        for c in characters:
            prompt += f"{c['name']}: {c['description']}\n"
        prompt += "\n"
    
    # 基本設定
    if settings:
        prompt += f"### 絶対守るべき設定:\n{settings}\n\n"
    
    # 表現レベル設定
    prompt += f"### 表現レベル設定:\n"
    prompt += f"- 淫語レベル: {explicit_level}% (値が高いほど直接的で卑猥な表現を使用)\n"
    prompt += f"- 描写詳細度: {detail_level}% (値が高いほど細部までの生々しい描写)\n"
    prompt += f"- 心理描写の深さ: {psychological_level}% (値が高いほど登場人物の内面を掘り下げる)\n\n"
    
    # 連続性指示（2話目以降）
    if episode_num > 1 and previous_summary:
        prompt += (
            "### 連続性の指示:\n"
            "- 前話からのキャラクターの関係性や状況を維持してください\n"
            "- 前のエピソードで始まったストーリーを自然に発展させてください\n"
            "- 登場人物の内面的変化や感情の変化を前のエピソードからの発展として描写してください\n"
            "- 前話との整合性を保ちながら物語を展開させてください\n\n"
        )
    
    # 執筆指示
    prompt += (
        "### 執筆指示:\n"
        "- 官能小説として魅力的で詳細な描写を心がけてください\n"
        "- 800〜1000文字程度で執筆してください\n"
        "- 各段落の最初は字下げし、会話文は「」で囲んでください\n"
        "- 適切に改行を入れて読みやすくしてください\n"
    )
    
    if episode_num == 1:
        prompt += "- 物語の導入として読者の興味を引く展開を心がけてください\n"
    else:
        prompt += "- 前話からの自然な流れを意識してください\n"
    
    return prompt