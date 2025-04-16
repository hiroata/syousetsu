#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Novel-related routes for the novel generator application.
Handles story generation, synopsis, and episode generation.
"""

import os
import json
import time
import datetime
import logging
import markdown
from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify, flash, current_app

# 一時的な修正: パッケージ構造が完成するまで直接utilsからインポート
from utils import (
    parse_synopsis, call_api_for_novel, get_episode_summary,
    generate_random_character_legacy
)
from services.novel_templates import (
    load_templates, get_template_by_id,
    load_writing_styles, get_style_by_id, get_random_murakami_style,
    load_story_structures, get_structure_by_id
)

# ロギングの設定
logger = logging.getLogger('novel_generator')

# Blueprint definition
novel_bp = Blueprint('novel', __name__)

########################################
# ルート: ホーム
########################################
@novel_bp.route('/')
def home():
    # 新しい小説を開始するために、セッションをクリア
    session.clear()
    return render_template('index.html')

########################################
# テンプレート取得: /templates
########################################
@novel_bp.route('/templates')
def get_templates():
    """利用可能なテンプレート一覧をJSON形式で返す"""
    templates = load_templates()
    return jsonify(templates)

########################################
# テンプレート適用: /apply_template/<template_id>
########################################
@novel_bp.route('/apply_template/<template_id>')
def apply_template(template_id):
    """指定されたテンプレートの内容を取得する"""
    template = get_template_by_id(template_id)
    if not template:
        return jsonify({"error": "テンプレートが見つかりません"}), 404
    return jsonify(template)

########################################
# 文体サンプル一覧: /writing_styles
########################################
@novel_bp.route('/writing_styles')
def get_writing_styles():
    """利用可能な文体サンプル一覧をJSON形式で返す"""
    styles = load_writing_styles()
    return jsonify(styles)

########################################
# 文体サンプル取得: /writing_style/<style_id>
########################################
@novel_bp.route('/writing_style/<style_id>')
def get_writing_style(style_id):
    """指定された文体サンプルを取得する"""
    style = get_style_by_id(style_id)
    if not style:
        return jsonify({"error": "文体サンプルが見つかりません"}), 404
    return jsonify(style)

########################################
# ストーリー構造一覧: /story_structures
########################################
@novel_bp.route('/story_structures')
def get_story_structures():
    """利用可能なストーリー構造テンプレート一覧をJSON形式で返す"""
    structures = load_story_structures()
    return jsonify(structures)

########################################
# ストーリー構造取得: /story_structure/<structure_id>
########################################
@novel_bp.route('/story_structure/<structure_id>')
def get_story_structure(structure_id):
    """指定されたストーリー構造テンプレートを取得する"""
    structure = get_structure_by_id(structure_id)
    if not structure:
        return jsonify({"error": "ストーリー構造テンプレートが見つかりません"}), 404
    return jsonify(structure)

########################################
# あらすじ生成: /generate_synopsis
########################################
@novel_bp.route('/generate_synopsis', methods=['POST'])
def generate_synopsis():
    try:
        start_time = time.time()
        logger.info("あらすじ生成開始")
        
        # フォーム入力の取得
        prompt = request.form.get('prompt', '')
        model_choice = request.form.get('model_choice', 'xai')  # デフォルトはxAI
        writing_style = request.form.get('writing_style', '村上龍風')  # デフォルトは村上龍風
        selected_structure = request.form.get('selected_structure', '')
        essential_settings = request.form.get('essential_settings', '')
        
        # 淫語レベル設定の取得
        explicit_level = request.form.get('explicit_level', '70')
        detail_level = request.form.get('detail_level', '80')
        psychological_level = request.form.get('psychological_level', '60')
        
        # キャラクター情報の取得と処理
        characters = []
        for i in range(1, 3):  # 最大2キャラクター
            name = request.form.get(f'character_name{i}', '').strip()
            desc = request.form.get(f'character_description{i}', '').strip()
            gender = request.form.get(f'character_gender{i}', 'male')
            kinks = request.form.get(f'character_kinks{i}', '')
            
            # ランダム生成が必要かチェック
            if name.startswith('【ランダム:') or (not name and not desc):
                # 名前も説明もない場合は完全ランダム生成
                name, desc = generate_random_character_legacy(gender, kinks)
            elif name and (not desc or desc.startswith('【ランダム生成】')):
                # 名前はあるが説明がない場合、説明だけランダム生成
                _, desc = generate_random_character_legacy(gender, kinks)
            
            if name:  # 名前がある場合のみキャラクターとして追加
                characters.append({'name': name, 'description': desc})
        
        # 生成用プロンプトの組み立て（あらすじ用）
        synopsis_prompt = "あなたは官能小説作家です。以下の設定に基づいて、官能小説の3話分のあらすじを作成してください。\n\n"
        synopsis_prompt += f"### メインプロンプト:\n{prompt}\n\n"
        
        # 村上龍風文体を指定
        murakami_style = get_random_murakami_style()
        synopsis_prompt += f"### 文体:\n{murakami_style['name']}の文体で書いてください。{murakami_style['description']}\n\n"
            
        if characters:
            synopsis_prompt += "### 登場人物:\n"
            for c in characters:
                synopsis_prompt += f"{c['name']}: {c['description']}\n"
            synopsis_prompt += "\n"
            
        if essential_settings:
            synopsis_prompt += f"### 絶対守るべき設定:\n{essential_settings}\n\n"
        
        # 淫語レベル設定を追加
        synopsis_prompt += f"### 表現レベル設定:\n"
        synopsis_prompt += f"- 淫語レベル: {explicit_level}% (値が高いほど直接的で卑猥な表現を使用)\n"
        synopsis_prompt += f"- 描写詳細度: {detail_level}% (値が高いほど細部までの生々しい描写)\n"
        synopsis_prompt += f"- 心理描写の深さ: {psychological_level}% (値が高いほど登場人物の内面を掘り下げる)\n\n"
        
        # ストーリー構造を追加
        if selected_structure:
            synopsis_prompt += f"### ストーリー構造:\n{selected_structure}構造で展開してください。\n\n"
        
        synopsis_prompt += (
            "### 指示:\n"
            "- 3話分のあらすじを作成してください\n"
            "- 各話は明確に「第1話:」「第2話:」「第3話:」などのラベルを付けてください\n"
            "- 各話は200〜300文字程度で簡潔に要約してください\n"
            "- 1話目は導入、2話目は展開、3話目はクライマックスになるよう構成してください\n"
            "- 官能描写のあるシーンは「〜〜という情事があった」など簡潔に示してください\n"
            "- 村上龍風の特徴である「生々しい描写」「都市の孤独」「機械的な性描写」などを活かしてください\n"
        )
        
        logger.info(f"あらすじ生成プロンプト: {len(synopsis_prompt)}文字")
        
        # API 呼び出しであらすじ生成
        synopsis_result = call_api_for_novel(model_choice, synopsis_prompt, max_tokens=1500)
        
        # あらすじを3つに分割（強化した解析関数を使用）
        synopsis_parts = parse_synopsis(synopsis_result)
        
        # セッションに保存
        session['prompt'] = prompt
        session['model_choice'] = model_choice
        session['writing_style'] = writing_style
        session['essential_settings'] = essential_settings
        session['characters'] = characters
        session['synopsis'] = synopsis_parts
        session['episodes'] = []
        session['explicit_level'] = explicit_level
        session['detail_level'] = detail_level
        session['psychological_level'] = psychological_level
        session['murakami_style'] = murakami_style['id']  # 使用する村上龍風のバリエーションを保存
        
        # JSONとして保存するためのシリアライズ
        synopsis_json = json.dumps(synopsis_parts)
        
        elapsed_time = time.time() - start_time
        logger.info(f"あらすじ生成完了: 所要時間={elapsed_time:.2f}秒")
        
        return render_template('synopsis.html', 
                              synopsis=synopsis_parts,
                              synopsis_json=synopsis_json,
                              prompt=prompt,
                              model_choice=model_choice,
                              writing_style=writing_style,
                              essential_settings=essential_settings,
                              characters=characters,
                              explicit_level=explicit_level,
                              detail_level=detail_level,
                              psychological_level=psychological_level,
                              datetime=datetime,
                              notification={
                                  'message': 'あらすじの生成が完了しました。内容を確認してください。',
                                  'type': 'success'
                              })
    except Exception as e:
        logger.error(f"あらすじ生成エラー: {e}", exc_info=True)
        # エラーページを表示
        return render_template('error.html', 
                              error_title='あらすじ生成エラー',
                              error_message=f'あらすじの生成中にエラーが発生しました: {str(e)}',
                              back_link='/',
                              datetime=datetime)

########################################
# あらすじ修正: /revise_synopsis
########################################
@novel_bp.route('/revise_synopsis', methods=['POST'])
def revise_synopsis():
    try:
        start_time = time.time()
        logger.info("あらすじ修正開始")
        
        revision_instructions = request.form.get('revision_instructions', '')
        prompt = request.form.get('prompt', '')
        model_choice = request.form.get('model_choice', 'xai')  # デフォルトはxAI
        writing_style = request.form.get('writing_style', '村上龍風')
        essential_settings = request.form.get('essential_settings', '')
        synopsis_data = request.form.get('synopsis_data', '{}')
        
        # 淫語レベル設定の取得
        explicit_level = request.form.get('explicit_level', '70')
        detail_level = request.form.get('detail_level', '80')
        psychological_level = request.form.get('psychological_level', '60')
        
        # キャラクター情報の取得
        characters = session.get('characters', [])
        
        # 現在のあらすじをJSONから復元
        try:
            current_synopsis = json.loads(synopsis_data)
        except:
            logger.error("あらすじJSONのパースに失敗")
            current_synopsis = {'episode1': '', 'episode2': '', 'episode3': ''}
        
        # 修正用プロンプトの組み立て
        revision_prompt = "あなたは官能小説作家です。以下の3話分のあらすじを修正指示に従って書き直してください。\n\n"
        revision_prompt += f"### 現在のあらすじ:\n\n"
        revision_prompt += f"第1話:\n{current_synopsis.get('episode1', '')}\n\n"
        revision_prompt += f"第2話:\n{current_synopsis.get('episode2', '')}\n\n"
        revision_prompt += f"第3話:\n{current_synopsis.get('episode3', '')}\n\n"
        revision_prompt += f"### 修正指示:\n{revision_instructions}\n\n"
        revision_prompt += f"### 元の設定:\n{prompt}\n\n"
        
        # 村上龍風文体を指定
        murakami_style_id = session.get('murakami_style', 'murakami_ryu_1')
        murakami_style = get_style_by_id(murakami_style_id) or get_random_murakami_style()
        revision_prompt += f"### 文体:\n{murakami_style['name']}の文体で書いてください。{murakami_style['description']}\n\n"
            
        if characters:
            revision_prompt += "### 登場人物:\n"
            for c in characters:
                revision_prompt += f"{c['name']}: {c['description']}\n"
            revision_prompt += "\n"
            
        if essential_settings:
            revision_prompt += f"### 絶対守るべき設定:\n{essential_settings}\n\n"
        
        # 淫語レベル設定を追加
        revision_prompt += f"### 表現レベル設定:\n"
        revision_prompt += f"- 淫語レベル: {explicit_level}% (値が高いほど直接的で卑猥な表現を使用)\n"
        revision_prompt += f"- 描写詳細度: {detail_level}% (値が高いほど細部までの生々しい描写)\n"
        revision_prompt += f"- 心理描写の深さ: {psychological_level}% (値が高いほど登場人物の内面を掘り下げる)\n\n"
        
        revision_prompt += (
            "### 指示:\n"
            "- 3話分のあらすじを修正指示に従って書き直してください\n"
            "- 各話は明確に「第1話:」「第2話:」「第3話:」などのラベルを付けてください\n"
            "- 各話は200〜300文字程度で簡潔に要約してください\n"
            "- 1話目は導入、2話目は展開、3話目はクライマックスになるよう構成してください\n"
            "- 官能描写のあるシーンは「〜〜という情事があった」など簡潔に示してください\n"
            "- 村上龍風の特徴である「生々しい描写」「都市の孤独」「機械的な性描写」などを活かしてください\n"
        )
        
        logger.info(f"あらすじ修正プロンプト: {len(revision_prompt)}文字")
        
        # API 呼び出しであらすじ修正
        revised_synopsis = call_api_for_novel(model_choice, revision_prompt, max_tokens=1500)
        
        # あらすじを3つに分割（強化した解析関数を使用）
        synopsis_parts = parse_synopsis(revised_synopsis)
        
        # セッションに保存
        session['prompt'] = prompt
        session['model_choice'] = model_choice
        session['writing_style'] = writing_style
        session['essential_settings'] = essential_settings
        session['characters'] = characters
        session['synopsis'] = synopsis_parts
        session['episodes'] = []
        session['explicit_level'] = explicit_level
        session['detail_level'] = detail_level
        session['psychological_level'] = psychological_level
        
        # JSONとして保存するためのシリアライズ
        synopsis_json = json.dumps(synopsis_parts)
        
        elapsed_time = time.time() - start_time
        logger.info(f"あらすじ修正完了: 所要時間={elapsed_time:.2f}秒")
        
        return render_template('synopsis.html', 
                              synopsis=synopsis_parts,
                              synopsis_json=synopsis_json,
                              prompt=prompt,
                              model_choice=model_choice,
                              writing_style=writing_style,
                              essential_settings=essential_settings,
                              characters=characters,
                              explicit_level=explicit_level,
                              detail_level=detail_level,
                              psychological_level=psychological_level,
                              datetime=datetime,
                              notification={
                                  'message': 'あらすじの修正が完了しました。内容を確認してください。',
                                  'type': 'success'
                              })
    except Exception as e:
        logger.error(f"あらすじ修正エラー: {e}", exc_info=True)
        # エラーページを表示
        return render_template('error.html', 
                              error_title='あらすじ修正エラー',
                              error_message=f'あらすじの修正中にエラーが発生しました: {str(e)}',
                              back_link='/',
                              datetime=datetime)

########################################
# 執筆開始: /start_writing
########################################
@novel_bp.route('/start_writing', methods=['POST'])
def start_writing():
    try:
        start_time = time.time()
        logger.info("第1話執筆開始")
        
        prompt = request.form.get('prompt', '')
        model_choice = request.form.get('model_choice', 'xai')  # デフォルトはxAI
        writing_style = request.form.get('writing_style', '村上龍風')
        essential_settings = request.form.get('essential_settings', '')
        synopsis_data = request.form.get('synopsis_data', '{}')
        
        # 淫語レベル設定の取得
        explicit_level = request.form.get('explicit_level', '70')
        detail_level = request.form.get('detail_level', '80')
        psychological_level = request.form.get('psychological_level', '60')
        
        # キャラクター情報の取得
        characters = session.get('characters', [])
        
        # あらすじをJSONから復元
        try:
            synopsis = json.loads(synopsis_data)
        except:
            logger.error("あらすじJSONのパースに失敗")
            synopsis = {'episode1': '', 'episode2': '', 'episode3': ''}
        
        # 村上龍風文体バリエーションの選択
        murakami_style_id = session.get('murakami_style', 'murakami_ryu_1')
        murakami_style = get_style_by_id(murakami_style_id) or get_random_murakami_style()
        
        # 第1話執筆用プロンプトの組み立て
        episode_prompt = "あなたは官能小説作家です。以下の設定と第1話のあらすじに基づいて、官能小説の第1話を執筆してください。\n\n"
        episode_prompt += f"### メインプロンプト:\n{prompt}\n\n"
        episode_prompt += f"### 第1話のあらすじ:\n{synopsis.get('episode1', '')}\n\n"
        
        # 文体指定
        episode_prompt += f"### 文体:\n{murakami_style['name']}の文体で書いてください。{murakami_style['description']}\n"
        episode_prompt += f"サンプル文: {murakami_style.get('sample', '')}\n\n"
            
        if characters:
            episode_prompt += "### 登場人物:\n"
            for c in characters:
                episode_prompt += f"{c['name']}: {c['description']}\n"
            episode_prompt += "\n"
            
        if essential_settings:
            episode_prompt += f"### 絶対守るべき設定:\n{essential_settings}\n\n"
        
        # 淫語レベル設定を追加
        episode_prompt += f"### 表現レベル設定:\n"
        episode_prompt += f"- 淫語レベル: {explicit_level}% (値が高いほど直接的で卑猥な表現を使用)\n"
        episode_prompt += f"- 描写詳細度: {detail_level}% (値が高いほど細部までの生々しい描写)\n"
        episode_prompt += f"- 心理描写の深さ: {psychological_level}% (値が高いほど登場人物の内面を掘り下げる)\n\n"
        
        episode_prompt += (
            "### 指示:\n"
            "- 官能小説として魅力的で詳細な描写を心がけてください\n"
            "- 800〜1000文字程度で執筆してください\n"
            "- 各段落の最初は字下げし、会話文は「」で囲んでください\n"
            "- 適切に改行を入れて読みやすくしてください\n"
            "- 村上龍風の特徴である「生々しい描写」「都市の孤独」「機械的な性描写」などを活かしてください\n"
            "- キャラクターの内面の葛藤や感情を丁寧に描写してください\n"
            "- 物語の導入として読者の興味を引く展開を心がけてください\n"
        )
        
        logger.info(f"第1話執筆プロンプト: {len(episode_prompt)}文字")
        
        # API 呼び出しで第1話執筆
        episode_text = call_api_for_novel(model_choice, episode_prompt, max_tokens=2000)
        
        # セッションに保存
        session['prompt'] = prompt
        session['model_choice'] = model_choice
        session['writing_style'] = writing_style
        session['essential_settings'] = essential_settings
        session['characters'] = characters
        session['synopsis'] = synopsis
        session['explicit_level'] = explicit_level
        session['detail_level'] = detail_level
        session['psychological_level'] = psychological_level
        
        # エピソード情報を保存
        episodes = session.get('episodes', [])
        episodes.append({
            'number': 1,
            'text': episode_text,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'style': murakami_style['name']
        })
        session['episodes'] = episodes
        
        # マークダウンからHTMLに変換
        episode_html = markdown.markdown(episode_text)
        
        elapsed_time = time.time() - start_time
        logger.info(f"第1話執筆完了: 所要時間={elapsed_time:.2f}秒, 文字数={len(episode_text)}")
        
        return render_template('result.html',
                              novel=episode_html,
                              episodes=episodes,
                              current_episode=1,
                              prompt=prompt,
                              writing_style=writing_style,
                              model_choice=model_choice,
                              explicit_level=explicit_level,
                              detail_level=detail_level,
                              psychological_level=psychological_level,
                              current_style=murakami_style['name'],
                              datetime=datetime,  # datetimeモジュールを追加
                              notification={
                                  'message': '第1話の執筆が完了しました。',
                                  'type': 'success'
                              })
    except Exception as e:
        logger.error(f"第1話執筆エラー: {e}", exc_info=True)
        # エラーページを表示
        return render_template('error.html', 
                              error_title='第1話執筆エラー',
                              error_message=f'第1話の執筆中にエラーが発生しました: {str(e)}',
                              back_link='/',
                              datetime=datetime)

########################################
# 次のエピソード生成: /next_episode
########################################
@novel_bp.route('/next_episode', methods=['POST'])
def next_episode():
    try:
        start_time = time.time()
        
        current_episode = int(request.form.get('current_episode', 1))
        logger.info(f"第{current_episode+1}話執筆開始")
        
        direction_request = request.form.get('direction_request', '')
        direction_tags = request.form.get('direction_tags', '')
        episode_style_choice = request.form.get('episode_style', 'auto')  # 文体選択を取得
        
        # セッションからデータ取得
        prompt = session.get('prompt', '')
        model_choice = session.get('model_choice', 'xai')
        writing_style = session.get('writing_style', '村上龍風')
        essential_settings = session.get('essential_settings', '')
        characters = session.get('characters', [])
        synopsis = session.get('synopsis', {})
        episodes = session.get('episodes', [])
        explicit_level = session.get('explicit_level', '70')
        detail_level = session.get('detail_level', '80')
        psychological_level = session.get('psychological_level', '60')
        
        # 次のエピソード番号
        next_episode_num = current_episode + 1
        
        # 村上龍風文体のバリエーション選択
        if episode_style_choice == 'auto' or episode_style_choice.startswith('murakami_ryu'):
            # 自動選択またはランダムな村上龍風バリエーション
            if episode_style_choice.startswith('murakami_ryu') and episode_style_choice != 'auto':
                # 特定のバリエーションが指定されている場合
                murakami_style = get_style_by_id(episode_style_choice) or get_random_murakami_style()
            else:
                # 自動選択の場合はランダム
                murakami_style = get_random_murakami_style()
        else:  # 団鬼六風など他の文体
            murakami_style = get_style_by_id(episode_style_choice) or get_random_murakami_style()
        
        # 対応するあらすじ取得 (3話以降は対応するあらすじがない場合あり)
        episode_synopsis_key = f'episode{next_episode_num}'
        episode_synopsis = synopsis.get(episode_synopsis_key, '')
        
        # 前話のテキスト取得
        previous_episode_text = ""
        if episodes and len(episodes) >= current_episode:
            previous_episode_text = episodes[current_episode - 1].get('text', '')
        
        # 前話の要約を生成
        previous_episode_summary = get_episode_summary(previous_episode_text, model_choice)
        
        # 次話執筆用プロンプトの組み立て
        episode_prompt = f"あなたは官能小説作家です。以下の設定と情報に基づいて、官能小説の第{next_episode_num}話を執筆してください。\n\n"
        episode_prompt += f"### メインプロンプト:\n{prompt}\n\n"
        
        # 3話目までならあらすじを使用
        if next_episode_num <= 3 and episode_synopsis:
            episode_prompt += f"### 第{next_episode_num}話のあらすじ:\n{episode_synopsis}\n\n"
        else:
            # 4話目以降は前のエピソードから展開を続ける
            episode_prompt += f"### 続編の執筆指示:\n前話までの流れを踏まえて、第{next_episode_num}話を自然な展開で書いてください。\n\n"
        
        # 選択されたタグがあれば追加
        if direction_tags:
            episode_prompt += f"### 次話の方向性タグ:\n{direction_tags}\n\n"
        
        # 方向性リクエストがあれば追加
        if direction_request:
            episode_prompt += f"### 方向性リクエスト:\n{direction_request}\n\n"
        
        # 前話の内容要約を提供
        episode_prompt += f"### 前話の内容要約:\n{previous_episode_summary}\n\n"
        
        # 選択された文体を指定
        episode_prompt += f"### 文体:\n{murakami_style['name']}の文体で書いてください。{murakami_style['description']}\n"
        episode_prompt += f"サンプル文: {murakami_style.get('sample', '')}\n\n"
        
        # 登場人物情報
        if characters:
            episode_prompt += "### 登場人物:\n"
            for c in characters:
                episode_prompt += f"{c['name']}: {c['description']}\n"
            episode_prompt += "\n"
        
        # 絶対守るべき設定
        if essential_settings:
            episode_prompt += f"### 絶対守るべき設定:\n{essential_settings}\n\n"
        
        # 淫語レベル設定を追加
        episode_prompt += f"### 表現レベル設定:\n"
        episode_prompt += f"- 淫語レベル: {explicit_level}% (値が高いほど直接的で卑猥な表現を使用)\n"
        episode_prompt += f"- 描写詳細度: {detail_level}% (値が高いほど細部までの生々しい描写)\n"
        episode_prompt += f"- 心理描写の深さ: {psychological_level}% (値が高いほど登場人物の内面を掘り下げる)\n\n"
        
        # 連続性を保つための指示
        episode_prompt += (
            "### 連続性の指示:\n"
            "- 前話からのキャラクターの関係性や状況を維持してください\n"
            "- 前のエピソードで始まったストーリーを自然に発展させてください\n"
            "- 登場人物の内面的変化や感情の変化を前のエピソードからの発展として描写してください\n"
            "- 前話との整合性を保ちながら物語を展開させてください\n\n"
        )
        
        episode_prompt += (
            "### 執筆指示:\n"
            "- 官能小説として魅力的で詳細な描写を心がけてください\n"
            "- 800〜1000文字程度で執筆してください\n"
            "- 各段落の最初は字下げし、会話文は「」で囲んでください\n"
            "- 適切に改行を入れて読みやすくしてください\n"
            "- 前話からの自然な流れを意識してください\n"
            "- 村上龍風の特徴である「生々しい描写」「都市の孤独」「機械的な性描写」などを活かしてください\n"
        )
        
        logger.info(f"第{next_episode_num}話執筆プロンプト: {len(episode_prompt)}文字")
        
        # API 呼び出しで次話執筆
        episode_text = call_api_for_novel(model_choice, episode_prompt, max_tokens=2000)
        
        # エピソード情報を保存
        episodes.append({
            'number': next_episode_num,
            'text': episode_text,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'style': murakami_style['name']
        })
        session['episodes'] = episodes
        
        # マークダウンからHTMLに変換
        episode_html = markdown.markdown(episode_text)
        
        elapsed_time = time.time() - start_time
        logger.info(f"第{next_episode_num}話執筆完了: 所要時間={elapsed_time:.2f}秒, 文字数={len(episode_text)}")
        
        return render_template('result.html',
                            novel=episode_html,
                            episodes=episodes,
                            current_episode=next_episode_num,
                            prompt=prompt,
                            writing_style=writing_style,
                            model_choice=model_choice,
                            explicit_level=explicit_level,
                            detail_level=detail_level,
                            psychological_level=psychological_level,
                            current_style=murakami_style['name'],
                            datetime=datetime,  # datetimeモジュールを追加
                            notification={
                                'message': f'第{next_episode_num}話の執筆が完了しました。',
                                'type': 'success'
                            })
    except Exception as e:
        logger.error(f"次話執筆エラー: {e}", exc_info=True)
        # エラーページを表示
        return render_template('error.html', 
                            error_title='次話執筆エラー',
                            error_message=f'次のエピソードの執筆中にエラーが発生しました: {str(e)}',
                            back_link=f'/view_episode/{current_episode}',
                            datetime=datetime)

########################################
# エピソード表示: /view_episode/<episode_num>
########################################
@novel_bp.route('/view_episode/<int:episode_num>')
def view_episode(episode_num):
    try:
        logger.info(f"エピソード表示: 第{episode_num}話")
        episodes = session.get('episodes', [])
        
        if not episodes or episode_num < 1 or episode_num > len(episodes):
            logger.warning(f"エピソード表示エラー: 第{episode_num}話は存在しません")
            return redirect(url_for('novel.home'))
        
        episode = episodes[episode_num - 1]
        episode_text = episode.get('text', '')
        episode_style = episode.get('style', '村上龍風')
        
        # マークダウンからHTMLに変換
        episode_html = markdown.markdown(episode_text)
        
        # すべての必要な変数をテンプレートに渡す
        return render_template('result.html',
                            novel=episode_html,
                            episodes=episodes,
                            current_episode=episode_num,
                            prompt=session.get('prompt', ''),
                            writing_style=session.get('writing_style', ''),
                            model_choice=session.get('model_choice', ''),
                            explicit_level=session.get('explicit_level', '70'),
                            detail_level=session.get('detail_level', '80'),
                            psychological_level=session.get('psychological_level', '60'),
                            current_style=episode_style,
                            datetime=datetime)  # datetimeモジュールを追加
    except Exception as e:
        logger.error(f"エピソード表示エラー: {e}", exc_info=True)
        # エラーページを表示
        return render_template('error.html', 
                            error_title='エピソード表示エラー',
                            error_message=f'エピソードの表示中にエラーが発生しました: {str(e)}',
                            back_link='/',
                            datetime=datetime)

########################################
# テキスト編集保存: /save_edited_episode
########################################
@novel_bp.route('/save_edited_episode', methods=['POST'])
def save_edited_episode():
    try:
        data = request.json
        episode_number = data.get('episode_number', 1)
        content = data.get('content', '')
        
        logger.info(f"エピソード編集保存: 第{episode_number}話")
        
        # エピソードのリストを取得
        episodes = session.get('episodes', [])
        
        # エピソード番号が範囲内かチェック
        if not episodes or episode_number < 1 or episode_number > len(episodes):
            logger.warning(f"エピソード編集保存エラー: 第{episode_number}話は存在しません")
            return jsonify({'error': 'エピソードが見つかりません'}), 404
        
        # エピソードを更新
        episodes[episode_number - 1]['text'] = content
        episodes[episode_number - 1]['edited'] = True  # 編集フラグを追加
        episodes[episode_number - 1]['edit_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['episodes'] = episodes
        
        # HTMLコンテンツを生成
        html_content = markdown.markdown(content)
        
        return jsonify({
            'success': True,
            'html_content': html_content,
            'message': '編集内容を保存しました'
        })
    except Exception as e:
        logger.error(f"エピソード編集保存エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# プロンプト保存: /save_prompt
########################################
@novel_bp.route('/save_prompt', methods=['POST'])
def save_prompt():
    try:
        data = request.json
        name = data.get('name', '')
        prompt = data.get('prompt', '')
        writing_style = data.get('writing_style', '村上龍風')
        essential_settings = data.get('essential_settings', '')
        model_choice = data.get('model_choice', 'xai')
        explicit_level = data.get('explicit_level', '70')
        detail_level = data.get('detail_level', '80')
        psychological_level = data.get('psychological_level', '60')
        save_type = data.get('save_type', 'settings-only')
        episodes = data.get('episodes', [])
        
        logger.info(f"プロンプト保存: {name}, タイプ: {save_type}")
        
        if not name:
            return jsonify({'error': 'プロンプト名が必要です'}), 400
        
        # 保存用データ作成
        prompt_data = {
            'name': name,
            'prompt': prompt,
            'writing_style': writing_style,
            'essential_settings': essential_settings,
            'model_choice': model_choice,
            'explicit_level': explicit_level,
            'detail_level': detail_level,
            'psychological_level': psychological_level,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'save_type': save_type
        }
        
        # 小説全体を保存する場合はエピソードも含める
        if save_type == 'full-novel' and episodes:
            prompt_data['episodes'] = episodes
        
        # ファイル名作成（スペースをアンダースコアに置換）
        filename = f"{name.replace(' ', '_')}_{int(datetime.datetime.now().timestamp())}.json"
        filepath = os.path.join(current_app.config['PROMPT_DIR'], filename)
        
        # データを保存
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, ensure_ascii=False, indent=2)
            return jsonify({'success': True, 'message': f'「{name}」として保存しました'})
        except Exception as e:
            logger.error(f"プロンプト保存ファイル書き込みエラー: {e}")
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"プロンプト保存エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# 保存プロンプト一覧: /saved_prompts
########################################
@novel_bp.route('/saved_prompts')
def list_saved_prompts():
    try:
        prompts = []
        for filename in os.listdir(current_app.config['PROMPT_DIR']):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(current_app.config['PROMPT_DIR'], filename), 'r', encoding='utf-8') as f:
                        prompt_data = json.load(f)
                        prompts.append({
                            'filename': filename,
                            'name': prompt_data.get('name', '名前なし'),
                            'timestamp': prompt_data.get('timestamp', ''),
                            'save_type': prompt_data.get('save_type', 'settings-only'),
                            'has_episodes': 'episodes' in prompt_data and len(prompt_data['episodes']) > 0,
                            'episode_count': len(prompt_data.get('episodes', [])),
                            'model_choice': prompt_data.get('model_choice', 'xai')
                        })
                except Exception as e:
                    logger.error(f"保存プロンプト読み込みエラー ({filename}): {e}")
                    continue
        
        # 新しい順に並べ替え
        prompts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify(prompts)
    except Exception as e:
        logger.error(f"保存プロンプト一覧エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# 保存プロンプト読み込み: /load_prompt/<filename>
########################################
@novel_bp.route('/load_prompt/<filename>')
def load_prompt(filename):
    try:
        filepath = os.path.join(current_app.config['PROMPT_DIR'], filename)
        if not os.path.exists(filepath):
            logger.warning(f"保存プロンプト読み込みエラー: ファイルが見つかりません: {filename}")
            return jsonify({'error': 'プロンプトが見つかりません'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            prompt_data = json.load(f)
            
        # 小説全体が保存されている場合はセッションに設定
        if 'episodes' in prompt_data and prompt_data.get('save_type') == 'full-novel':
            session['episodes'] = prompt_data['episodes']
            
        return jsonify(prompt_data)
    except Exception as e:
        logger.error(f"保存プロンプト読み込みエラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# 保存プロンプト一覧ページ: /saved_prompts_page
########################################
@novel_bp.route('/saved_prompts_page')
def saved_prompts_page():
    return render_template('saved_prompts.html', datetime=datetime)

########################################
# 文体適用: /apply_writing_style
########################################
@novel_bp.route('/apply_writing_style', methods=['POST'])
def apply_writing_style():
    """生成されたテキストに指定の文体を適用する"""
    try:
        data = request.json
        style_id = data.get('style_id')
        text = data.get('text', '')
        
        logger.info(f"文体適用: {style_id}, テキスト長: {len(text)}文字")
        
        if not style_id or not text:
            return jsonify({"error": "スタイルIDとテキストが必要です"}), 400
        
        # 文体の取得
        style = get_style_by_id(style_id)
        if not style:
            return jsonify({"error": "無効な文体IDです"}), 400
            
        # 文体変換用プロンプト作成
        prompt = f"""
あなたは文体変換の専門家です。以下のテキストを「{style['name']}」の文体に変換してください。

### 変換対象テキスト:
{text}

### 目標とする文体の特徴:
{style['description']}

### 文体サンプル:
{style.get('sample', '')}

### 指示:
- 内容は保持しつつ、文体のみを変換してください
- 段落構造や会話の構造は維持してください
- 官能的な表現や描写のニュアンスは保持してください
- 原文と同程度の長さを維持してください
"""
        
        # モデル選択してAPIを呼び出す
        model_choice = session.get('model_choice', 'openai')
        converted_text = call_api_for_novel(model_choice, prompt, max_tokens=2000)
        
        return jsonify({"success": True, "converted_text": converted_text})
    except Exception as e:
        logger.error(f"文体適用エラー: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500