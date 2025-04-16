<<<<<<< HEAD
# kannou
=======
# 小説生成ツール

最新のAIモデルを活用して小説を生成するWebアプリケーションです。Grok-3、Gemini 2.5 Pro、Claude 3.5、GPT-4など複数のAIモデルに対応しています。

## 🌟 機能

- 様々なジャンルの小説を自動生成
- プロットアイデアの提案
- 複数のエピソードを継続して執筆
- 複数の最新AIモデルに対応
- モバイル対応のレスポンシブデザイン

## 📚 デモ

[GitHub Pages版](https://[your-username].github.io/syousetsu/)でブラウザから直接お試しいただけます。

デモモードではAPIキーなしで基本機能を体験できます。実際のAI生成には各サービスのAPIキーが必要です。

## 🚀 アーキテクチャ

このプロジェクトは2つの主要コンポーネントで構成されています：

1. **フロントエンド** (GitHub Pagesでホスティング)
   - HTML/CSS/JavaScript
   - ローカルストレージによるセッション管理
   - 各種AIモデルの管理UIとレンダリング

2. **バックエンドAPI** (別サービスでホスティング)
   - Flask RESTful API
   - 各種AIモデルへのプロキシ
   - Grok-3、Gemini 2.5 Pro、Claude 3.5、GPT-4対応

## 🔧 セットアップ方法

### フロントエンド（ローカルテスト）

```bash
# リポジトリをクローン
git clone https://github.com/[your-username]/syousetsu.git
cd syousetsu

# 任意のHTTPサーバーでdocsディレクトリを配信
# 例：Pythonの組み込みHTTPサーバー
cd docs
python -m http.server 8000
```

ブラウザで http://localhost:8000 にアクセスしてください。

### バックエンドAPI（開発環境）

```bash
# APIディレクトリに移動
cd api

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して各APIキーを設定

# サーバー起動
python app.py
```

APIサーバーは http://localhost:5000 で起動します。

## 🔑 APIキーの取得方法

各AIモデルを利用するには、対応するAPIキーが必要です：

- **xAI (Grok-3)**: [x.ai](https://x.ai/) からAPIキーを取得
- **Google (Gemini 2.5)**: [Google AI Studio](https://makersuite.google.com/app/apikey) からAPIキーを取得
- **Anthropic (Claude 3.5)**: [Anthropic Console](https://console.anthropic.com/settings/keys) からAPIキーを取得
- **OpenAI (GPT-4)**: [OpenAI Platform](https://platform.openai.com/api-keys) からAPIキーを取得

取得したAPIキーは `.env` ファイルに設定してください。

## 🚀 デプロイ

### フロントエンド（GitHub Pages）

1. リポジトリの「Settings」→「Pages」を開く
2. Source を「GitHub Actions」に設定

`main` ブランチにプッシュすると、GitHub Actionsにより自動的に `docs` ディレクトリの内容がデプロイされます。

### バックエンドAPI（Render.com）

1. [Render.com](https://render.com/) でアカウント作成
2. 「New Web Service」を選択
3. GitHubリポジトリと連携
4. 以下の設定を行う:
   - Name: `novel-ai-api` など
   - Environment: `Python`
   - Build Command: `pip install -r api/requirements.txt`
   - Start Command: `cd api && gunicorn app:app`
   - Add Environment Variables: `.env` ファイルの内容を設定

設定完了後、自動的にデプロイが開始されます。

## ⚙️ 環境変数

`.env` ファイルに設定する環境変数：

```
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# OpenAI API Key
OPENAI_API_KEY=sk-xxxxx

# Google Gemini API Key
GEMINI_API_KEY=AIzaSyxxxxx

# DeepSeek API Key
DEEPSEEK_API_KEY=sk-xxxxx

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# xAI API Key
XAI_API_KEY=xai-xxxxx

# 管理者用シークレットキー（レート制限リセット用）
ADMIN_SECRET_KEY=your-secret-admin-key
```

## 📱 使用方法

1. ジャンルを選択
2. 使用するAIモデルを選択
3. お題やキャラクターなどを入力
4. 「物語を生成」ボタンをクリック
5. 生成された小説が表示され、「次の話を執筆」ボタンで続きを生成可能

## 🛠️ 技術スタック

- **フロントエンド**: HTML5, CSS3, JavaScript (Vanilla)
- **バックエンド**: Python, Flask, Flask-CORS
- **AI API**: xAI (Grok-3), Google (Gemini 2.5 Pro), Anthropic (Claude 3.5), OpenAI (GPT-4)
- **デプロイ**: GitHub Pages, Render.com
- **その他**: Markdown, LocalStorage

## 📄 ライセンス

MIT

## 🤝 貢献

プルリクエスト大歓迎です！新機能の追加、バグ修正、ドキュメント改善など、どんな貢献でもお待ちしています。

## 📞 連絡先

質問や提案がある場合は、[Issues](https://github.com/[your-username]/syousetsu/issues) に投稿してください。

## 📚 デモ

[GitHub Pages版](https://[your-username].github.io/syousetsu/?debug=true)でブラウザから直接お試しいただけます。

デモモードではAPIキーなしで基本機能を体験できます。実際のAI生成には各サービスのAPIキーが必要です。
>>>>>>> bb454308762095c1d2860583bbc24cdaf7d8492f
