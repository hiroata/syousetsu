#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogue service for the novel generator application.
Provides dialogue templates for various styles and themes.
"""

import random
import logging
from typing import Dict, List, Any, Optional, Union

# ロギングの設定
logger = logging.getLogger('novel_generator')

# 団鬼六風のドスケベ長文淫語セリフ（テーマ別テンプレート）
DAN_ONIROKU_STYLE_DIALOGUES = {
    "禁断の関係": [
        "あなたのその柔肌は、触れるたびに私を狂わせる。こんな関係、許されるはずがないのに…あなたの濡れた唇が、私の理性を溶かすんだ。さあ、跪け。私のチンポをその小さな口で咥えるんだ。舌を絡ませて、喉の奥まで飲み込むんだよ。苦しいか？　その涙目がたまらない。お前はもう、私の所有物だ。ベッドに押し倒して、その細い腰を掴み、後ろから激しく突き上げてやる。ほら、お前のアソコが私のものを締め付けるたびに、いやらしい汁が溢れてくる。感じすぎて腰が砕けるまで、犯してやるよ。お前の喘ぎ声が、私の欲望をさらに煽るんだ。もっと叫べ、私に服従するんだ。",
        "この禁じられた関係が、私たちを狂わせる。あなたのその白い首筋に唇を這わせ、乳房を揉みしだくたびに、我慢なんてできなくなるんだ。お前のその細い指が、私のチンポを握る感触…もうたまらないよ。脚を開け、私を受け入れろ。お前の濡れたアソコに、私のものをゆっくり押し込んでやる。感じるだろう？　私たちの関係が禁じられているほど、この快楽は深い。お前の喘ぎ声が、私の耳に響くたびに、もっと激しく腰を振ってしまうんだ。もっと奥まで突いて、お前を私のものに染め上げるよ。お前がイキ果てるまで、止めてやらないからな。"
    ],
    "身体への執着": [
        "あぁ、お前のその豊満な乳房…手に収まりきらないほど柔らかくて、乳首がこんなに硬く尖ってる。舌で転がすたびに、お前の身体がビクビク震えるのがたまらないよ。もっと感じてくれ。私の指が、お前の内腿を這い、秘部に触れると、もう濡れそぼってるじゃないか。脚を開け、私のチンポを受け入れる準備をしろ。ゆっくりと押し込んでやるよ。お前の内壁が、私のものをギュッと締め付けるたびに、快楽が全身を貫くんだ。もっと深く、もっと激しく突いてやる。お前が泣き叫ぶまで、奥まで貫いてやるからな。私の精液で、お前の子宮を満たしてやるよ。",
        "お前のそのエロい身体、犯さずにはいられないよ。ほら、尻を突き出せ。私が後ろからガンガン突いてやる。お前のアソコに、私のチンポをぶち込んで、根元まで押し込むたびに、お前が喘ぐ声が止まらない。もっと腰を振れよ、私のものを締め付けてくれ。感じすぎて頭がおかしくなるまで、イカせてやるからな。お前のそのいやらしい汁が、私の太ももまで滴り落ちてるぜ。さあ、もっと大声で喘げ。私に犯される快感を、全身で味わえよ。最後はお前の奥に熱い精液をぶちまけて、妊娠する勢いで注ぎ込んでやる。"
    ],
    "痛みと快楽の境界": [
        "お前は私の玩具だ。さあ、四つん這いになって、そのエロい尻を差し出せ。私が叩くたびに赤く染まる肌が、たまらなく美しいよ。痛いか？　でも、お前のアソコはもっと濡れてるじゃないか。変態だな。私のチンポを咥え込めよ、後ろからガツガツ突いてやる。お前の内壁が、私のものを締め付けるたびに、快楽が脳まで響くんだ。もっと叫べ、もっと私を欲しがれ。お前が壊れるまで突きまくってやるよ。最後はお前の奥に精液をぶちまけて、私の痕跡を刻み込んでやるからな。",
        "お前のその柔らかい肌を、私の指が這うたびに、微かな震えが走る。痛みと快楽の狭間で、お前は私に服従するんだ。さあ、ベッドに横たわれ。私が上から覆いかぶさり、お前の乳首を噛みながら、チンポを奥まで突き刺してやる。お前の喘ぎ声が、私の耳元で響くたびに、もっと激しく腰を振ってしまうんだ。お前が泣き叫ぶまで、止めてやらないからな。私の精液で、お前を満たしてやるよ。"
    ],
    "背徳感と情欲": [
        "こんな場所で、こんな時間に…お前を抱くなんて、正気じゃないかもしれない。でも、お前のその白い首筋に唇を這わせ、乳房を揉みしだくたびに、我慢なんてできなくなるんだ。お前のその細い指が、私のチンポを握る感触…もうたまらないよ。脚を開け、私を受け入れろ。お前の濡れたアソコに、私のものをゆっくり押し込んでやる。感じるだろう？　私たちの関係が禁じられているほど、この快楽は深い。お前の喘ぎ声が、私の耳に響くたびに、もっと激しく腰を振ってしまうんだ。もっと奥まで突いて、お前を私のものに染め上げるよ。お前がイキ果てるまで、止めてやらないからな。",
        "お前のその罪深い身体、私を狂わせる。お前は私のものだ。さあ、ベッドに押し倒して、その細い腰を掴み、後ろから激しく突き上げてやる。ほら、お前のアソコが私のものを締め付けるたびに、いやらしい汁が溢れてくる。感じすぎて腰が砕けるまで、犯してやるよ。お前の喘ぎ声が、私の欲望をさらに煽るんだ。もっと叫べ、私に服従するんだ。"
    ]
}

# 汎用的なセリフ（テーマに縛られないテンプレート）
GENERAL_EROTIC_DIALOGUES = [
    "あなたのその柔肌は、触れるたびに私を狂わせる。こんな関係、許されるはずがないのに…あなたの濡れた唇が、私の理性を溶かすんだ。",
    "あぁ、お前のその豊満な乳房…手に収まりきらないほど柔らかくて、乳首がこんなに硬く尖ってる。舌で転がすたびに、お前の身体がビクビク震えるのがたまらないよ。",
    "お前のそのエロい身体、犯さずにはいられないよ。ほら、尻を突き出せ。私が後ろからガンガン突いてやる。",
    "お前は私の玩具だ。さあ、四つん這いになって、そのエロい尻を差し出せ。私が叩くたびに赤く染まる肌が、たまらなく美しいよ。",
    "こんな場所で、こんな時間に…お前を抱くなんて、正気じゃないかもしれない。でも、お前のその白い首筋に唇を這わせ、乳房を揉みしだくたびに、我慢なんてできなくなるんだ。"
]

def get_dialogue_by_theme(theme: str) -> str:
    """
    テーマに基づいた団鬼六風のセリフを取得
    
    Args:
        theme: ダイアログのテーマ
        
    Returns:
        str: 団鬼六風のセリフ
    """
    if theme in DAN_ONIROKU_STYLE_DIALOGUES:
        return random.choice(DAN_ONIROKU_STYLE_DIALOGUES[theme])
    else:
        # テーマが見つからない場合は汎用的なセリフから選ぶ
        return random.choice(GENERAL_EROTIC_DIALOGUES)

def get_random_dialogue() -> str:
    """
    ランダムな官能セリフを取得
    
    Returns:
        str: ランダムな官能セリフ
    """
    # すべてのテーマからランダムに選ぶ
    all_themes = list(DAN_ONIROKU_STYLE_DIALOGUES.keys())
    return get_dialogue_by_theme(random.choice(all_themes))

def generate_dialogue_prompt(theme: Optional[str] = None, character_name: Optional[str] = None) -> str:
    """
    AIに官能的なセリフを生成させるためのプロンプトを作成
    
    Args:
        theme: セリフのテーマ（オプション）
        character_name: キャラクターの名前（オプション）
        
    Returns:
        str: 生成用プロンプト
    """
    prompt = "あなたは官能小説作家です。以下の条件に基づいて、官能的なセリフを生成してください。\n\n"
    
    if theme:
        prompt += f"### テーマ:\n{theme}\n\n"
    
    if character_name:
        prompt += f"### 話者:\n{character_name}\n\n"
    
    prompt += "### 参考セリフ:\n"
    prompt += get_random_dialogue() + "\n\n"
    
    prompt += """
### 指示:
- 200〜300字程度の官能的なセリフを1つ生成してください
- 比喩表現を多用し、感覚的な描写を心がけてください
- 直接的な性描写を含めてください
- 相手の身体への執着や欲望を表現してください
- 会話調で、一人称は「私」または「俺」を使ってください
"""
    
    return prompt