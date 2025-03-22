from flask import Flask, request, render_template, session, jsonify
import requests
import os
import markdown
import re
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 任意のシークレットキーを設定
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 各種APIキーの設定
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
XAI_API_KEY = os.getenv('XAI_API_KEY')

# APIクライアントの初期化
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

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
    
    # モデルの選択
    model_choice = request.form.get('model_choice', 'openai')
    ideas = ""

    try:
        if model_choice == 'openrouter':
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Novel Generator"
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300
                }
            )
            if response.status_code == 200:
                ideas = response.json()["choices"][0]["message"]["content"]

        elif model_choice == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            ideas = response.choices[0].message.content

        elif model_choice == 'gemini':
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            ideas = response.text

        elif model_choice == 'deepseek':
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            ideas = response.choices[0].message.content

        elif model_choice == 'anthropic':
            response = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            ideas = response.content[0].text

        else:  # xai
            headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json={
                    "model": "grok-2-1212",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300
                }
            )
            if response.status_code == 200:
                ideas = response.json()["choices"][0]["message"]["content"]

        if not ideas:
            return jsonify({"success": False, "error": "アイデアを生成できませんでした"})

        return jsonify({"success": True, "ideas": ideas})

    except Exception as e:
        return jsonify({"success": False, "error": f"エラー: {str(e)}"})

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

    # モデルの選択
    model_choice = request.form.get('model_choice', 'openai')
    novel_text = ""

    try:
        if model_choice == 'openrouter':
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Novel Generator"
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": 700
                }
            )
            if response.status_code == 200:
                novel_text = response.json()["choices"][0]["message"]["content"]

        elif model_choice == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=700
            )
            novel_text = response.choices[0].message.content

        elif model_choice == 'gemini':
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(full_prompt)
            novel_text = response.text

        elif model_choice == 'deepseek':
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=700
            )
            novel_text = response.choices[0].message.content

        elif model_choice == 'anthropic':
            response = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=700,
                messages=[{"role": "user", "content": full_prompt}]
            )
            novel_text = response.content[0].text

        else:  # xai
            headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json={
                    "model": "grok-2-1212",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": 700
                }
            )
            if response.status_code == 200:
                novel_text = response.json()["choices"][0]["message"]["content"]

        if not novel_text:
            raise Exception("テキストの生成に失敗しました")

        novel_html = markdown.markdown(novel_text)

    except Exception as e:
        novel_html = f"エラー: {str(e)}"
        novel_text = novel_html

    # 要約生成（選択されたモデルと同じモデルを使用）
    summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{novel_text}"
    summary = ""

    try:
        if model_choice == 'openrouter':
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": summary_prompt}],
                    "max_tokens": 100
                }
            )
            if response.status_code == 200:
                summary = response.json()["choices"][0]["message"]["content"]

        elif model_choice == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=100
            )
            summary = response.choices[0].message.content

        elif model_choice == 'gemini':
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(summary_prompt)
            summary = response.text

        elif model_choice == 'deepseek':
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=100
            )
            summary = response.choices[0].message.content

        elif model_choice == 'anthropic':
            response = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary = response.content[0].text

        else:  # xai
            headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json={
                    "model": "grok-2-1212",
                    "messages": [{"role": "user", "content": summary_prompt}],
                    "max_tokens": 100
                }
            )
            if response.status_code == 200:
                summary = response.json()["choices"][0]["message"]["content"]

        if not summary:
            raise Exception("要約の生成に失敗しました")

    except Exception as e:
        summary = f"要約失敗: {str(e)}"

    # セッションに保存
    story_list = session.get('story_list', [])
    story_list.append({'text': novel_text, 'summary': summary, 'title': f"第{len(story_list) + 1}話"})
    session['story_list'] = story_list
    session['prompt'] = prompt
    session['genre'] = genre
    session['instructions'] = instructions
    session['story_request'] = story_request
    session['font_choice'] = font_choice
    session['model_choice'] = model_choice  # モデル選択を保存

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

        # モデルの選択（セッションから取得）
        model_choice = session.get('model_choice', 'openai')
        new_text = ""

        try:
            if model_choice == 'openrouter':
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:5000",
                    "X-Title": "Novel Generator"
                }
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "openai/gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": full_prompt}],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    new_text = response.json()["choices"][0]["message"]["content"]

            elif model_choice == 'openai':
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                new_text = response.choices[0].message.content

            elif model_choice == 'gemini':
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(full_prompt)
                new_text = response.text

            elif model_choice == 'deepseek':
                response = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                new_text = response.choices[0].message.content

            elif model_choice == 'anthropic':
                response = anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                new_text = response.content[0].text

            else:  # xai
                headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "grok-2-1212",
                        "messages": [{"role": "user", "content": full_prompt}],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    new_text = response.json()["choices"][0]["message"]["content"]

            if not new_text:
                raise Exception("テキストの生成に失敗しました")

            new_html = markdown.markdown(new_text)

            # 要約生成（同じモデルを使用）
            summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{new_text}"
            summary = ""

            try:
                if model_choice == 'openrouter':
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json={
                            "model": "openai/gpt-3.5-turbo",
                            "messages": [{"role": "user", "content": summary_prompt}],
                            "max_tokens": 100
                        }
                    )
                    if response.status_code == 200:
                        summary = response.json()["choices"][0]["message"]["content"]

                elif model_choice == 'openai':
                    response = openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": summary_prompt}],
                        max_tokens=100
                    )
                    summary = response.choices[0].message.content

                elif model_choice == 'gemini':
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(summary_prompt)
                    summary = response.text

                elif model_choice == 'deepseek':
                    response = deepseek_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": summary_prompt}],
                        max_tokens=100
                    )
                    summary = response.choices[0].message.content

                elif model_choice == 'anthropic':
                    response = anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=100,
                        messages=[{"role": "user", "content": summary_prompt}]
                    )
                    summary = response.content[0].text

                else:  # xai
                    response = requests.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers=headers,
                        json={
                            "model": "grok-2-1212",
                            "messages": [{"role": "user", "content": summary_prompt}],
                            "max_tokens": 100
                        }
                    )
                    if response.status_code == 200:
                        summary = response.json()["choices"][0]["message"]["content"]

                if not summary:
                    raise Exception("要約の生成に失敗しました")

            except Exception as e:
                summary = f"要約失敗: {str(e)}"

        except Exception as e:
            new_html = f"エラー: {str(e)}"
            new_text = new_html
            summary = "要約失敗"

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