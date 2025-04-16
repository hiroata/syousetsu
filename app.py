from flask import Flask, request, render_template, session, jsonify
import requests
import os
import markdown
import re
from io import BytesIO
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 任意のシークレットキーを設定
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 各種APIキーの取得
xai_api_key = os.getenv('XAI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

# Gemini APIの設定
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# OpenAIクライアントの初期化
openai_client = None
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)

# Anthropicクライアントの初期化
anthropic_client = None
if anthropic_api_key:
    anthropic_client = Anthropic(api_key=anthropic_api_key)

# ホーム画面
@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

# プロット生成アシスト
@app.route('/assist', methods=['POST'])
def assist_plot():
    genre = request.form.get('genre', '')
    model_choice = request.form.get('model_choice', 'xai')
    
    # ジャンル別のプロットアイデア生成
    prompt = f"以下のジャンル「{genre}」に合った面白い小説のプロットアイデアを3つ提案してください。各アイデアには、簡単な概要、主要登場人物案、物語の舞台を含めてください。"
    
    if model_choice == 'xai':
        # xAI (Grok-3) APIリクエスト
        headers = {"Authorization": f"Bearer {xai_api_key}", "Content-Type": "application/json"}
        data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            ideas = response.json().get("choices", [{}])[0].get("message", {}).get("content", "アイデアを生成できませんでした")
            return jsonify({"success": True, "ideas": ideas})
        else:
            return jsonify({"success": False, "error": f"エラー: {response.status_code}"})
            
    elif model_choice == 'gemini':
        # Google Gemini 2.5 Pro
        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
            
            model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                         generation_config={"temperature": 0.7, "max_output_tokens": 1000},
                                         safety_settings=safety_settings)
            response = model.generate_content(prompt)
            return jsonify({"success": True, "ideas": response.text})
        except Exception as e:
            return jsonify({"success": False, "error": f"Geminiエラー: {str(e)}"})
            
    elif model_choice == 'anthropic':
        # Anthropic Claude
        try:
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return jsonify({"success": True, "ideas": message.content[0].text})
        except Exception as e:
            return jsonify({"success": False, "error": f"Anthropicエラー: {str(e)}"})
            
    elif model_choice == 'openai':
        # OpenAI GPT-4
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return jsonify({"success": True, "ideas": response.choices[0].message.content})
        except Exception as e:
            return jsonify({"success": False, "error": f"OpenAIエラー: {str(e)}"})
            
    else:
        return jsonify({"success": False, "error": "サポートされていないモデルが選択されました"})

# 小説生成
@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    genre = request.form.get('genre', '')
    instructions = request.form.get('instructions', '')
    story_request = request.form.get('story_request', '')
    font_choice = request.form.get('font_choice', 'sans')
    model_choice = request.form.get('model_choice', 'xai')
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

    novel_text = None
    error_message = None
    
    # 選択されたモデルに基づいて小説を生成
    if model_choice == 'xai':
        # xAI (Grok-3) APIリクエスト
        headers = {"Authorization": f"Bearer {xai_api_key}", "Content-Type": "application/json"}
        data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": full_prompt}], "max_tokens": 1500}
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            novel_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "テキストが見つかりませんでした")
        else:
            error_message = f"エラー: {response.status_code} - {response.text}"
            
    elif model_choice == 'gemini':
        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                         generation_config={"temperature": 0.7, "max_output_tokens": 1500})
            response = model.generate_content(full_prompt)
            novel_text = response.text
        except Exception as e:
            error_message = f"Geminiエラー: {str(e)}"
            
    elif model_choice == 'anthropic':
        try:
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            novel_text = message.content[0].text
        except Exception as e:
            error_message = f"Anthropicエラー: {str(e)}"
            
    elif model_choice == 'openai':
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            novel_text = response.choices[0].message.content
        except Exception as e:
            error_message = f"OpenAIエラー: {str(e)}"
    
    # エラーチェック
    if error_message:
        novel_html = error_message
        novel_text = error_message
    else:
        novel_html = markdown.markdown(novel_text)

    # 要約生成（小説テキストが生成された場合のみ）
    summary = "要約失敗"
    if novel_text and not error_message:
        summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{novel_text}"
        
        if model_choice == 'xai':
            data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 100}
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
            if response.status_code == 200:
                summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "要約失敗")
        elif model_choice == 'gemini':
            try:
                model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                            generation_config={"temperature": 0.3, "max_output_tokens": 100})
                response = model.generate_content(summary_prompt)
                summary = response.text
            except:
                pass
        elif model_choice == 'anthropic':
            try:
                message = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=100,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ]
                )
                summary = message.content[0].text
            except:
                pass
        elif model_choice == 'openai':
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                summary = response.choices[0].message.content
            except:
                pass

    # セッションに保存
    story_list = session.get('story_list', [])
    story_list.append({'text': novel_text, 'summary': summary, 'title': f"第{len(story_list) + 1}話", 'model': model_choice})
    session['story_list'] = story_list
    session['prompt'] = prompt
    session['genre'] = genre
    session['instructions'] = instructions
    session['story_request'] = story_request
    session['font_choice'] = font_choice
    session['model_choice'] = model_choice

    return render_template('result.html', novel=novel_html, story_list=story_list, characters=characters, prompt=prompt, genre=genre, instructions=instructions, story_request=story_request, font_choice=font_family, model_choice=model_choice)

# 続きの生成
@app.route('/continue_story', methods=['GET'])
@app.route('/continue_story/', methods=['GET']) # スラッシュ付きでも対応
def continue_story():
    try:
        prompt = session.get('prompt', '')
        genre = session.get('genre', '')
        instructions = session.get('instructions', '')
        story_request = session.get('story_request', '')
        font_choice = session.get('font_choice', 'sans')
        model_choice = session.get('model_choice', 'xai')
        story_list = session.get('story_list', [])
        characters = session.get('characters', [])
        font_family = 'Noto Sans JP' if font_choice == 'sans' else 'Noto Serif JP'

        if not story_list:
            return "ストーリーが見つかりません", 404

        # 直前のエピソードの要約を取得
        previous_summary = story_list[-1]['summary']
        episode_number = len(story_list) + 1

        # 続きのプロンプト
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

        new_text = None
        error_message = None
        
        # 選択されたモデルに基づいて続きを生成
        if model_choice == 'xai':
            # xAI (Grok-3) APIリクエスト
            headers = {"Authorization": f"Bearer {xai_api_key}", "Content-Type": "application/json"}
            data = {
                "model": "grok-3-beta", 
                "messages": [{"role": "user", "content": full_prompt}], 
                "max_tokens": 1500,
                "temperature": 0.7
            }
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
            
            if response.status_code == 200:
                new_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "テキストが見つかりませんでした")
            else:
                error_message = f"エラー: {response.status_code} - {response.text}"
                
        elif model_choice == 'gemini':
            try:
                model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                           generation_config={"temperature": 0.7, "max_output_tokens": 1500})
                response = model.generate_content(full_prompt)
                new_text = response.text
            except Exception as e:
                error_message = f"Geminiエラー: {str(e)}"
                
        elif model_choice == 'anthropic':
            try:
                message = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1500,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                new_text = message.content[0].text
            except Exception as e:
                error_message = f"Anthropicエラー: {str(e)}"
                
        elif model_choice == 'openai':
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=1500,
                    temperature=0.7
                )
                new_text = response.choices[0].message.content
            except Exception as e:
                error_message = f"OpenAIエラー: {str(e)}"
        
        # エラーチェック
        if error_message:
            new_html = error_message
            new_text = error_message
        else:
            new_html = markdown.markdown(new_text)

        # 要約生成（新テキストが生成された場合のみ）
        summary = "要約失敗"
        if new_text and not error_message:
            summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{new_text}"
            
            if model_choice == 'xai':
                data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 100}
                response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
                if response.status_code == 200:
                    summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "要約失敗")
            elif model_choice == 'gemini':
                try:
                    model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                                generation_config={"temperature": 0.3, "max_output_tokens": 100})
                    response = model.generate_content(summary_prompt)
                    summary = response.text
                except:
                    pass
            elif model_choice == 'anthropic':
                try:
                    message = anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=100,
                        temperature=0.3,
                        messages=[
                            {"role": "user", "content": summary_prompt}
                        ]
                    )
                    summary = message.content[0].text
                except:
                    pass
            elif model_choice == 'openai':
                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[{"role": "user", "content": summary_prompt}],
                        max_tokens=100,
                        temperature=0.3
                    )
                    summary = response.choices[0].message.content
                except:
                    pass

        # セッションに追加
        story_list.append({'text': new_text, 'summary': summary, 'title': f"第{episode_number}話", 'model': model_choice})
        session['story_list'] = story_list

        return render_template('result.html', novel=new_html, story_list=story_list, characters=characters, prompt=prompt, genre=genre, instructions=instructions, story_request=story_request, font_choice=font_family, model_choice=model_choice)
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
    return render_template('result.html', novel=novel_html, story_list=story_list, characters=session.get('characters', []), prompt=session.get('prompt', ''), genre=session.get('genre', ''), instructions=session.get('instructions', ''), story_request=session.get('story_request', ''), font_choice=session.get('font_choice', 'Noto Sans JP'), model_choice=session.get('model_choice', 'xai'))

if __name__ == "__main__":
    app.run(debug=True)