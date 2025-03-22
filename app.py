from flask import Flask, request, render_template, session, jsonify
import requests
import os
import markdown
import re
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 任意のシークレットキーを設定
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# xAI APIキー
api_key = os.getenv('XAI_API_KEY')

# ホーム画面
@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

# プロット生成アシスト
@app.route('/assist', methods=['POST'])
def assist_plot():
    genre = request.form.get('genre', '')
    
    # ジャンル別のプロットアイデア生成
    prompt = f"以下のジャンル「{genre}」に合った面白い小説のプロットアイデアを3つ提案してください。各アイデアには、簡単な概要、主要登場人物案、物語の舞台を含めてください。"
    
    # APIリクエスト
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "grok-2-1212", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        ideas = response.json().get("choices", [{}])[0].get("message", {}).get("content", "アイデアを生成できませんでした")
        return jsonify({"success": True, "ideas": ideas})
    else:
        return jsonify({"success": False, "error": f"エラー: {response.status_code}"})

# 小説生成
@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    genre = request.form.get('genre', '')
    instructions = request.form.get('instructions', '')
    story_request = request.form.get('story_request', '')
    font_choice = request.form.get('font_choice', 'sans')
    font_family = 'Noto Sans JP' if font_choice == 'sans' else 'Noto Serif JP'

    # キャラクター保存
    characters = session.get('characters', [])
    if 'character_name' in request.form and request.form['character_name'].strip():
        characters.append({
            'name': request.form['character_name'],
            'description': request.form['character_description']
        })
        session['characters'] = characters

    # プロンプト構築
    full_prompt = f"あなたは小説の設定を考案するプロフェッショナルです。\n\nジャンル: {genre}\n\n{prompt}"
    if instructions:
        full_prompt += f"\n\n### 指示:\n{instructions}"
    if story_request:
        full_prompt += f"\n\n### ストーリー展開のリクエスト:\n{story_request}"
    if characters:
        full_prompt += "\n\n### 登場キャラクター:\n" + "\n".join([f"{c['name']}: {c['description']}" for c in characters])
    full_prompt += "\n\n約700文字で第1話を生成してください。プロットではなく、実際の物語として書いてください。各段落の最初は全角スペースで字下げし、会話文は「」で囲み、適切に改行してください。"

    # APIリクエスト
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "grok-2-1212", "messages": [{"role": "user", "content": full_prompt}], "max_tokens": 700}
    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        novel_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "テキストが見つかりませんでした")
        novel_html = markdown.markdown(novel_text)
    else:
        novel_html = f"エラー: {response.status_code} - {response.text}"
        novel_text = novel_html

    # 要約生成
    summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{novel_text}"
    data = {"model": "grok-2-1212", "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 100}
    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
    summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "") if response.status_code == 200 else "要約失敗"

    # セッションに保存
    story_list = session.get('story_list', [])
    story_list.append({'text': novel_text, 'summary': summary, 'title': f"第{len(story_list) + 1}話"})
    session['story_list'] = story_list
    session['prompt'] = prompt
    session['genre'] = genre
    session['instructions'] = instructions
    session['story_request'] = story_request
    session['font_choice'] = font_choice

    return render_template('result.html', novel=novel_html, story_list=story_list, characters=characters, prompt=prompt, genre=genre, instructions=instructions, story_request=story_request, font_choice=font_family)

# 続きの生成 (完全に新しいエピソードとして)
@app.route('/continue_story', methods=['GET'])
@app.route('/continue_story/', methods=['GET']) # スラッシュ付きでも対応
def continue_story():
    try:
        prompt = session.get('prompt', '')
        genre = session.get('genre', '')
        instructions = session.get('instructions', '')
        story_request = session.get('story_request', '')
        font_choice = session.get('font_choice', 'sans')
        story_list = session.get('story_list', [])
        characters = session.get('characters', [])
        font_family = 'Noto Sans JP' if font_choice == 'sans' else 'Noto Serif JP'

        if not story_list:
            return "ストーリーが見つかりません", 404

        # 直前のエピソードの要約を取得
        previous_summary = story_list[-1]['summary']
        episode_number = len(story_list) + 1

        # 続きのプロンプト - 重要な変更点
        full_prompt = f"""あなたは小説の設定を考案するプロフェッショナルです。

ジャンル: {genre}

以下のようなストーリーの続編となる「第{episode_number}話」を書いてください。
前回のあらすじ: {previous_summary}

この第{episode_number}話は、前回の続きですが、完全に新しいエピソードとして書いてください。
前回の内容をそのまま繰り返すのではなく、ストーリーを前に進めてください。
約700〜1000文字の新しいエピソードを書いてください。

各段落の最初は全角スペースで字下げし、会話文は「」で囲み、適切に改行してください。"""

        if instructions:
            full_prompt += f"\n\n### 指示:\n{instructions}"
        if story_request:
            full_prompt += f"\n\n### ストーリー展開のリクエスト:\n{story_request}"
        if characters:
            full_prompt += "\n\n### 登場キャラクター:\n" + "\n".join([f"{c['name']}: {c['description']}" for c in characters])

        # APIリクエスト - トークン数を増やす
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "grok-2-1212", 
            "messages": [{"role": "user", "content": full_prompt}], 
            "max_tokens": 1000,  # トークン数を増やす
            "temperature": 0.7   # 創造性のパラメータを少し上げる
        }
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            # 新しいテキストだけを取得（前の内容を引き継がないようにする）
            new_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "テキストが見つかりませんでした")
            new_html = markdown.markdown(new_text)
        else:
            new_html = f"エラー: {response.status_code} - {response.text}"
            new_text = new_html

        # 要約生成
        summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{new_text}"
        data = {"model": "grok-2-1212", "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 100}
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "") if response.status_code == 200 else "要約失敗"

        # セッションに追加
        story_list.append({'text': new_text, 'summary': summary, 'title': f"第{episode_number}話"})
        session['story_list'] = story_list

        return render_template('result.html', novel=new_html, story_list=story_list, characters=characters, prompt=prompt, genre=genre, instructions=instructions, story_request=story_request, font_choice=font_family)
    except Exception as e:
        # エラーメッセージを返す
        return f"エラーが発生しました: {str(e)}", 500

# ストーリー履歴の閲覧
@app.route('/story/<int:story_index>')
def view_story(story_index):
    story_list = session.get('story_list', [])
    if story_index >= len(story_list):
        return "ストーリーが見つかりません", 404
    novel_html = markdown.markdown(story_list[story_index]['text'])
    return render_template('result.html', novel=novel_html, story_list=story_list, characters=session.get('characters', []), prompt=session.get('prompt', ''), genre=session.get('genre', ''), instructions=session.get('instructions', ''), story_request=session.get('story_request', ''), font_choice=session.get('font_choice', 'Noto Sans JP'))

if __name__ == "__main__":
    app.run(debug=True)