#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Character utilities for the novel generator application.
Provides functions for character generation and management.
"""

import random
import logging
from typing import Dict, List, Tuple, Any, Optional

# ロギングの設定
logger = logging.getLogger('novel_generator')

def generate_random_character(gender: str) -> Dict[str, Any]:
    """
    ランダムなキャラクター設定を生成する
    
    Args:
        gender: 性別 ('male' または 'female')
        
    Returns:
        Dict[str, Any]: キャラクター情報の辞書
    """
    # 性別に基づく名前とベース設定
    if gender == "male":
        names = ["健太", "翔", "大輔", "剛", "悠真", "拓也", "直樹", "隆", "良介", "祐介", 
                "誠", "哲也", "一郎", "健", "修二", "徹", "竜也", "和彦", "浩二", "洋介"]
        age_range = (25, 45)
        occupations = ["会社員", "フリーランス", "写真家", "教師", "IT技術者", "医師", "建築家", 
                     "デザイナー", "飲食店オーナー", "作家", "営業マン", "プログラマー", "カメラマン", 
                     "弁護士", "パイロット", "大学講師", "フォトグラファー", "起業家"]
        body_types = ["筋肉質", "細身だが鍛えている", "がっしりとした体格", "背が高く精悍", "整った体型", 
                     "少しぽっちゃりした体型", "筋肉隆々", "細マッチョ", "骨太", "肩幅広め", 
                     "スラっとした体型", "バランスのとれた体格"]
        personalities = ["冷静", "情熱的", "謎めいた", "優しい", "支配的", "自信に満ちた", "内向的だが芯が強い", 
                       "知的", "寡黙", "穏やか", "慎重", "大胆", "繊細", "温厚", "クール", "思慮深い"]
        backgrounds = [
            "東京の高層ビル群で働き、成功を収めているが内面は空虚",
            "地方出身で上京し、都会の厳しさと快楽を知った",
            "学生時代から才能を認められ、若くして成功を収めた",
            "挫折を経験し、人生の意味を探している",
            "裕福な家庭で育ったが、自分の道を見つけるために家を出た",
            "海外での経験が豊富で、様々な文化を体験してきた",
            "孤独な幼少期を過ごし、大人になっても心の傷を抱えている",
            "仕事一筋で生きてきたが、最近人生の転機を迎えている"
        ]
    else:  # female
        names = ["美咲", "愛", "沙織", "加奈子", "恵", "美波", "由香", "麻衣", "瑞希", "彩",
                "優子", "瞳", "香織", "奈々", "裕子", "綾", "真理子", "菜々子", "由美", "美香"]
        age_range = (22, 38)
        occupations = ["OL", "モデル", "看護師", "デザイナー", "フリーランス", "教師", "カフェ店員", 
                     "フローリスト", "アーティスト", "編集者", "広告代理店勤務", "インテリアコーディネーター", 
                     "Web担当", "美容師", "ジュエリーデザイナー", "客室乗務員", "ホテルコンシェルジュ", "秘書"]
        body_types = ["細身", "スレンダー", "均整のとれた体", "豊満", "小柄だがくびれがある", "胸が大きく腰が細い",
                     "やわらかな曲線美", "すらっとした手足", "アスリート体型", "華奢", "グラマラス", 
                     "モデル体型", "ほっそりとした"]
        personalities = ["控えめ", "好奇心旺盛", "情熱的", "神秘的", "知的", "感受性豊か", "内に秘めた欲望を持つ",
                       "芯の強い", "素直", "華やか", "積極的", "物静か", "クール", "天真爛漫", "しっかり者", "優雅"]
        backgrounds = [
            "都会で一人暮らしを始め、自由と孤独を知る",
            "厳格な家庭で育ち、抑圧された欲望を解放しようとしている",
            "周囲からの期待に応え続け、本当の自分を見失っている",
            "仕事で成功を収め、プライベートでも充実を求めている",
            "過去の失恋から立ち直り、新たな恋を探している",
            "好奇心旺盛で様々な経験を求めている",
            "地方から上京し、都会での新生活に期待と不安を抱えている",
            "完璧主義で周囲からの評価を気にしすぎる傾向がある"
        ]
    
    # ランダムな特性を選択
    name = random.choice(names)
    age = random.randint(*age_range)
    occupation = random.choice(occupations)
    appearance = random.choice(body_types)
    personality = random.choice(personalities)
    background = random.choice(backgrounds)
    
    # キャラクターの設定を辞書にまとめる
    character = {
        'name': name,
        'gender': gender,
        'age': age,
        'occupation': occupation,
        'appearance': appearance,
        'personality': personality,
        'background': background,
        'kinks': '',
        'tags': '',
        'speech_pattern': ''
    }
    
    logger.info(f"ランダムキャラクター生成: {name}({gender})")
    
    return character

def generate_character_description(character: Dict[str, Any]) -> str:
    """
    キャラクター情報から説明文を生成する
    
    Args:
        character: キャラクター情報の辞書
        
    Returns:
        str: キャラクターの説明文
    """
    name = character.get('name', '')
    age = character.get('age', '')
    gender = character.get('gender', '')
    occupation = character.get('occupation', '')
    appearance = character.get('appearance', '')
    personality = character.get('personality', '')
    background = character.get('background', '')
    
    description = f"{name}（{age}歳）は{occupation}。"
    
    if appearance:
        description += f"{appearance}で、"
    
    if personality:
        description += f"性格は{personality}。"
    else:
        description += "。"
    
    if background:
        description += f" {background}。"
    
    # 性癖があれば追加
    kinks = character.get('kinks', '')
    if kinks:
        description = f"【性癖: {kinks}】\n" + description
    
    return description

def enrich_character(character: Dict[str, Any], prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    キャラクター設定を充実させるためのAIプロンプトを生成
    
    Args:
        character: 基本的なキャラクター情報
        prompt: カスタムプロンプト (オプション)
        
    Returns:
        Dict[str, Any]: AIに渡すためのプロンプト
    """
    # デフォルトプロンプト
    default_prompt = f"""
あなたは小説のキャラクター設定の専門家です。以下の基本情報を元に、キャラクターの背景や特徴を充実させてください。

### 基本情報:
- 名前: {character.get('name', '')}
- 性別: {character.get('gender', '')}
- 年齢: {character.get('age', '')}
- 職業: {character.get('occupation', '')}
- 外見: {character.get('appearance', '')}
- 性格: {character.get('personality', '')}

### 指示:
- キャラクターの過去や背景について詳細を追加してください
- 特徴的な癖や習慣があれば追加してください
- このキャラクターの欲望や内面的な葛藤を描写してください
- 会話の特徴や口調の特徴があれば記述してください
- 官能小説に適した要素を追加してください
"""
    
    if prompt:
        return prompt
    return default_prompt