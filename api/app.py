from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

app = Flask(__name__)
CORS(app)  # GitHub Pagesからのリクエストを許可

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

# レート制限のための簡易カウンター（本番環境ではRedisなどを使用）
request_counter = {
    'count': 0,
    'limit': 100  # 1時間あたりの最大リクエスト数
}

@app.route('/')
def home():
    return jsonify({'status': 'active', 'message': '小説生成APIサーバー稼働中'})

@app.route('/api/ideas', methods=['POST'])
def generate_ideas():
    # レート制限チェック
    if request_counter['count'] >= request_counter['limit']:
        return jsonify({'success': False, 'error': 'レート制限を超えました。しばらく経ってから再試行してください。'}), 429
    
    request_counter['count'] += 1
    
    data = request.json
    genre = data.get('genre', '')
    model_choice = data.get('model_choice', 'xai')
    
    # ジャンル別のプロットアイデア生成
    prompt = f"以下のジャンル「{genre}」に合った面白い小説のプロットアイデアを3つ提案してください。各アイデアには、簡単な概要、主要登場人物案、物語の舞台を含めてください。"
    
    try:
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
                
        elif model_choice == 'anthropic':
            # Anthropic Claude
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return jsonify({"success": True, "ideas": message.content[0].text})
                
        elif model_choice == 'openai':
            # OpenAI GPT-4
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return jsonify({"success": True, "ideas": response.choices[0].message.content})
                
        else:
            return jsonify({"success": False, "error": "サポートされていないモデルが選択されました"})
    
    except Exception as e:
        return jsonify({"success": False, "error": f"エラーが発生しました: {str(e)}"}), 500

@app.route('/api/generate', methods=['POST'])
def generate_story():
    # レート制限チェック
    if request_counter['count'] >= request_counter['limit']:
        return jsonify({'success': False, 'error': 'レート制限を超えました。しばらく経ってから再試行してください。'}), 429
    
    request_counter['count'] += 1
    
    data = request.json
    prompt = data.get('prompt', '')
    genre = data.get('genre', '')
    instructions = data.get('instructions', '')
    story_request = data.get('story_request', '')
    model_choice = data.get('model_choice', 'xai')
    characters = data.get('characters', [])
    
    # プロンプト構築
    full_prompt = f"あなたは小説の設定を考案するプロフェッショナルです。\n\nジャンル: {genre}\n\n{prompt}"
    if instructions:
        full_prompt += f"\n\n### 指示:\n{instructions}"
    if story_request:
        full_prompt += f"\n\n### ストーリー展開のリクエスト:\n{story_request}"
    if characters:
        full_prompt += "\n\n### 登場キャラクター:\n" + "\n".join([f"{c['name']}: {c['description']}" for c in characters])
    full_prompt += "\n\n約700文字で第1話を生成してください。プロットではなく、実際の物語として書いてください。各段落の最初は全角スペースで字下げし、会話文は「」で囲み、適切に改行してください。"
    
    try:
        novel_text = None
        
        # 選択されたモデルに基づいて小説を生成
        if model_choice == 'xai':
            # xAI (Grok-3) APIリクエスト
            headers = {"Authorization": f"Bearer {xai_api_key}", "Content-Type": "application/json"}
            data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": full_prompt}], "max_tokens": 1500}
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
            
            if response.status_code == 200:
                novel_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "テキストが見つかりませんでした")
            else:
                return jsonify({"success": False, "error": f"エラー: {response.status_code}"})
                
        elif model_choice == 'gemini':
            model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                         generation_config={"temperature": 0.7, "max_output_tokens": 1500})
            response = model.generate_content(full_prompt)
            novel_text = response.text
                
        elif model_choice == 'anthropic':
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            novel_text = message.content[0].text
                
        elif model_choice == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            novel_text = response.choices[0].message.content
        
        # 要約生成
        summary = "要約失敗"
        if novel_text:
            summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{novel_text}"
            
            if model_choice == 'xai':
                data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 100}
                response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
                if response.status_code == 200:
                    summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "要約失敗")
            elif model_choice == 'gemini':
                model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                            generation_config={"temperature": 0.3, "max_output_tokens": 100})
                response = model.generate_content(summary_prompt)
                summary = response.text
            elif model_choice == 'anthropic':
                message = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=100,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ]
                )
                summary = message.content[0].text
            elif model_choice == 'openai':
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                summary = response.choices[0].message.content
        
        return jsonify({
            "success": True,
            "novel_text": novel_text,
            "summary": summary,
            "title": "第1話",
            "model": model_choice
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": f"エラーが発生しました: {str(e)}"}), 500

@app.route('/api/continue', methods=['POST'])
def continue_story():
    # レート制限チェック
    if request_counter['count'] >= request_counter['limit']:
        return jsonify({'success': False, 'error': 'レート制限を超えました。しばらく経ってから再試行してください。'}), 429
    
    request_counter['count'] += 1
    
    data = request.json
    prompt = data.get('prompt', '')
    genre = data.get('genre', '')
    instructions = data.get('instructions', '')
    story_request = data.get('story_request', '')
    model_choice = data.get('model_choice', 'xai')
    previous_summary = data.get('previous_summary', '')
    episode_number = data.get('episode_number', 2)
    characters = data.get('characters', [])
    
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
    
    try:
        new_text = None
        
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
                return jsonify({"success": False, "error": f"エラー: {response.status_code}"})
                
        elif model_choice == 'gemini':
            model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                       generation_config={"temperature": 0.7, "max_output_tokens": 1500})
            response = model.generate_content(full_prompt)
            new_text = response.text
                
        elif model_choice == 'anthropic':
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            new_text = message.content[0].text
                
        elif model_choice == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            new_text = response.choices[0].message.content
        
        # 要約生成
        summary = "要約失敗"
        if new_text:
            summary_prompt = f"以下のストーリーの要約を100文字以内で作成してください。\n\n{new_text}"
            
            if model_choice == 'xai':
                data = {"model": "grok-3-beta", "messages": [{"role": "user", "content": summary_prompt}], "max_tokens": 100}
                response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
                if response.status_code == 200:
                    summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "要約失敗")
            elif model_choice == 'gemini':
                model = genai.GenerativeModel(model_name="gemini-2.5-pro-preview-03-25", 
                                            generation_config={"temperature": 0.3, "max_output_tokens": 100})
                response = model.generate_content(summary_prompt)
                summary = response.text
            elif model_choice == 'anthropic':
                message = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=100,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ]
                )
                summary = message.content[0].text
            elif model_choice == 'openai':
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                summary = response.choices[0].message.content
        
        return jsonify({
            "success": True,
            "novel_text": new_text,
            "summary": summary,
            "title": f"第{episode_number}話",
            "model": model_choice
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": f"エラーが発生しました: {str(e)}"}), 500

# デモモード用（実際のAPIキーが不要）
@app.route('/api/demo/generate', methods=['POST'])
def demo_generate():
    data = request.json
    model_choice = data.get('model_choice', 'xai')
    
    # デモ用の固定テキスト
    demo_text = """　山田太郎は窓際の席に座り、教室の外を見つめていた。魔法学園「星風学園」の入学式から一週間が経ち、ようやく授業にも慣れてきたところだった。しかし彼の心には常に不安があった。他の生徒たちは、入学前から基礎的な魔法を習得しているのに対し、太郎は魔法の才能に目覚めたのがつい最近だったからだ。

　「次の実技試験、どうしよう...」

　太郎はため息をつきながら呟いた。明日は初めての実技試験があり、基本的な火の魔法を披露しなければならない。彼は何度も練習したが、うまく火を灯すことができなかった。

　「大丈夫？なんだか元気ないね」

　突然、後ろから声をかけられ太郎は振り向いた。そこには、クラスメイトの佐藤美咲が立っていた。彼女は入学してすぐに評判になった天才少女で、どんな魔法も難なくこなすと言われていた。

　「ああ、ちょっと明日の実技試験のことを考えてて...」

　「練習手伝おうか？私、火の魔法得意だよ」

　美咲は満面の笑みで言った。太郎は驚いたが、ありがたく申し出を受けることにした。"""
    
    # デモ用の固定要約
    demo_summary = "魔法学園の新入生・山田太郎が実技試験を前に不安を抱えるが、天才少女・佐藤美咲の手助けを受けることになる。"
    
    return jsonify({
        "success": True,
        "novel_text": demo_text,
        "summary": demo_summary,
        "title": "第1話（デモ）",
        "model": model_choice
    })

@app.route('/api/demo/continue', methods=['POST'])
def demo_continue():
    data = request.json
    episode_number = data.get('episode_number', 2)
    model_choice = data.get('model_choice', 'xai')
    
    # デモ用の固定テキスト
    demo_continuation = """　翌日、太郎は緊張しながら実技試験に臨んだ。教室の中央に立ち、深呼吸をしてから美咲に教わった通りに魔力を集中させる。

　「集中して、呼吸を整えて...」

　太郎は心の中で唱えながら、手のひらに魔力を集めていった。すると、指先から小さな炎が灯り、やがてそれは美しい火の玉へと成長した。

　「見事です、山田くん」

　試験官のグリフィス先生が微笑んだ。太郎は成功の喜びに顔をほころばせた。教室の後ろで見ていた美咲も親指を立てて健闘を讃えている。

　試験の後、太郎は美咲にお礼を言うために校庭に向かった。しかし、そこで彼は不思議な光景を目にする。美咲が一人で立ち、手から青い光を放っていたのだ。普通の魔法とは明らかに違う、古代魔法の輝きだった。

　「これは...」

　太郎が思わず声を出すと、美咲はハッとして振り返った。彼女の目には一瞬、人間離れした光が宿ったように見えた。"""
    
    # デモ用の固定要約
    demo_summary = "太郎は美咲の助けで実技試験に合格するが、後に彼女が古代魔法を使う不思議な姿を目撃してしまう。"
    
    return jsonify({
        "success": True,
        "novel_text": demo_continuation,
        "summary": demo_summary,
        "title": f"第{episode_number}話（デモ）",
        "model": model_choice
    })

@app.route('/api/demo/ideas', methods=['POST'])
def demo_ideas():
    data = request.json
    genre = data.get('genre', '')
    
    # デモ用のアイデア
    demo_ideas = f"""アイデア1:
概要：{genre}のジャンルで、隠された才能に目覚めた主人公が、古代の秘密を守る組織に招かれる物語
登場人物：山田太郎：18歳、普通の高校生だが特殊な能力の兆候がある、佐藤美咲：古代組織のメンバーで主人公を見守る少女
舞台：現代の東京と古代の力が残る秘密の場所

アイデア2:
概要：{genre}のジャンルで、記憶を失った主人公が、自分の過去と世界の危機に関わる真実を探る旅
登場人物：鈴木一郎：記憶喪失の青年、高橋花子：謎の協力者で過去を知っている
舞台：謎の力で変容した近未来の日本

アイデア3:
概要：{genre}のジャンルで、特殊な能力を持つ人々が集まる学校で起こる不思議な事件と成長の物語
登場人物：田中誠：能力に目覚めたばかりの新入生、渡辺先生：謎めいた過去を持つ指導教官
舞台：能力者育成のための隔離された学園「星風学院」"""
    
    return jsonify({"success": True, "ideas": demo_ideas})

# システム状態API
@app.route('/api/status', methods=['GET'])
def api_status():
    api_health = {
        'xai': xai_api_key is not None,
        'openai': openai_api_key is not None,
        'anthropic': anthropic_api_key is not None,
        'gemini': gemini_api_key is not None,
        'server_version': '1.0.0',
        'request_count': request_counter['count'],
        'request_limit': request_counter['limit']
    }
    
    return jsonify(api_health)

# レート制限リセット（開発用・本番では定期的なcronジョブなどで処理）
@app.route('/api/admin/reset_limit', methods=['POST'])
def reset_rate_limit():
    # 簡易的な認証（本番では適切な認証を実装）
    auth_key = request.headers.get('X-Admin-Key')
    if auth_key != os.getenv('ADMIN_SECRET_KEY', 'dev_admin_key'):
        return jsonify({'success': False, 'error': '認証エラー'}), 401
    
    request_counter['count'] = 0
    return jsonify({'success': True, 'message': 'レート制限をリセットしました'})

if __name__ == "__main__":
    app.run(debug=True)