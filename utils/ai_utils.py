#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI API utilities for the novel generator application.
These functions handle the interaction with various AI service providers.
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, Union
from datetime import datetime

# ロギングの設定
logger = logging.getLogger('novel_generator')

def call_api_for_novel(model_choice: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """
    モデル選択に応じて各AIサービスのAPIを呼び出す関数
    
    Args:
        model_choice: 使用するAIモデルの種類 ('xai', 'grok-3', 'gpt-4o', 'claude-3-opus', 'deepseek-v3')
        user_prompt: AIに送信するプロンプト
        max_tokens: 生成する最大トークン数
        
    Returns:
        str: AIからの応答テキスト
    """
    # 各APIキーを取得 (load_dotenv() で .env から自動ロード)
    xai_api_key = os.getenv('XAI_API_KEY', '')
    openai_api_key = os.getenv('OPENAI_API_KEY', '')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
    
    # サポートされているモデルの確認
    supported_models = ['xai', 'grok-3', 'gpt-4o', 'claude-3-opus', 'deepseek-v3']
    if model_choice not in supported_models:
        logger.warning(f"未サポートのモデル '{model_choice}' が指定されました。デフォルト(xAI)を使用します。")
        model_choice = 'xai'
    
    # リトライ設定
    max_retries = 3
    retry_delay = 2  # 秒
    
    for retry in range(max_retries):
        try:
            # xAI (Grok) モデル
            if model_choice in ['xai', 'grok-3']:
                if not xai_api_key:
                    raise ValueError("xAI APIキーが設定されていません")
                    
                headers = {"Authorization": f"Bearer {xai_api_key}", "Content-Type": "application/json"}
                
                # モデルを識別子から選択
                if model_choice == 'grok-3':
                    model_id = "grok-3-1212"  # Grok-3モデル識別子
                else:  # デフォルトはgrok-2
                    model_id = "grok-2-1212"
                    
                data = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": user_prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                endpoint = "https://api.x.ai/v1/chat/completions"
                
                logger.info(f"xAI API呼び出し: モデル={model_id}, max_tokens={max_tokens}")
                resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
                if resp.status_code == 200:
                    result = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "テキスト取得失敗")
                    logger.info(f"xAI API応答: {len(result)}文字")
                    return result
                else:
                    error_msg = f"xAI APIエラー: ステータスコード={resp.status_code}, レスポンス={resp.text}"
                    logger.error(error_msg)
                    if retry < max_retries - 1:
                        logger.info(f"xAI API: {retry + 1}回目のリトライ...")
                        time.sleep(retry_delay)
                        continue
                    return f"エラー: {resp.status_code} - {resp.text}"
                
            # OpenAI GPT-4o モデル
            elif model_choice == 'gpt-4o':
                if not openai_api_key:
                    raise ValueError("OpenAI APIキーが設定されていません")
                
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openai_api_key}"}
                
                data = {
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": user_prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.8
                }
                endpoint = "https://api.openai.com/v1/chat/completions"
                
                logger.info(f"OpenAI API呼び出し: モデル=gpt-4o, max_tokens={max_tokens}")
                resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
                if resp.status_code == 200:
                    result = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "テキスト取得失敗")
                    logger.info(f"OpenAI API応答: {len(result)}文字")
                    return result
                else:
                    error_msg = f"OpenAI APIエラー: ステータスコード={resp.status_code}, レスポンス={resp.text}"
                    logger.error(error_msg)
                    if retry < max_retries - 1:
                        logger.info(f"OpenAI API: {retry + 1}回目のリトライ...")
                        time.sleep(retry_delay)
                        continue
                    return f"エラー: {resp.status_code} - {resp.text}"
                
            # Anthropic Claude 3 Opus モデル
            elif model_choice == 'claude-3-opus':
                if not anthropic_api_key:
                    raise ValueError("Anthropic APIキーが設定されていません")
                
                headers = {
                    "x-api-key": anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "claude-3-opus-20240229",
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ]
                }
                endpoint = "https://api.anthropic.com/v1/messages"
                
                logger.info(f"Anthropic API呼び出し: モデル=claude-3-opus-20240229, max_tokens={max_tokens}")
                resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
                if resp.status_code == 200:
                    result = resp.json().get("content", [{}])[0].get("text", "テキスト取得失敗")
                    logger.info(f"Anthropic API応答: {len(result)}文字")
                    return result
                else:
                    error_msg = f"Anthropic APIエラー: ステータスコード={resp.status_code}, レスポンス={resp.text}"
                    logger.error(error_msg)
                    if retry < max_retries - 1:
                        logger.info(f"Anthropic API: {retry + 1}回目のリトライ...")
                        time.sleep(retry_delay)
                        continue
                    return f"エラー: {resp.status_code} - {resp.text}"
            
            # DeepSeek V3-0324 モデル
            elif model_choice == 'deepseek-v3':
                if not deepseek_api_key:
                    raise ValueError("DeepSeek APIキーが設定されていません")
                
                headers = {
                    "Authorization": f"Bearer {deepseek_api_key}",
                    "Content-Type": "application/json"
                }
                
                # 現在の日付を取得してシステムプロンプトに追加
                today = datetime.now().strftime("%m月%d日")
                
                data = {
                    "model": "deepseek-chat",  # 正しいモデル識別子
                    "messages": [
                        # システムプロンプトを追加
                        {"role": "system", "content": f"该助手为DeepSeek Chat，由深度求索公司创造。今天是{today}。"},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7  # 0.7を指定すると内部では0.21として処理される
                }
                
                # DeepSeek APIのベースURLを.envから取得（デフォルト値も設定）
                deepseek_api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
                endpoint = f"{deepseek_api_base}/chat/completions"
                
                logger.info(f"DeepSeek API呼び出し: モデル=deepseek-chat, max_tokens={max_tokens}")
                resp = requests.post(endpoint, headers=headers, json=data, timeout=60)
                if resp.status_code == 200:
                    result = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "テキスト取得失敗")
                    logger.info(f"DeepSeek API応答: {len(result)}文字")
                    return result
                else:
                    error_msg = f"DeepSeek APIエラー: ステータスコード={resp.status_code}, レスポンス={resp.text}"
                    logger.error(error_msg)
                    if retry < max_retries - 1:
                        logger.info(f"DeepSeek API: {retry + 1}回目のリトライ...")
                        time.sleep(retry_delay)
                        continue
                    return f"エラー: {resp.status_code} - {resp.text}"

            else:
                error_msg = f"未知のモデル: {model_choice}"
                logger.error(error_msg)
                return error_msg

        except Exception as e:
            logger.error(f"API呼び出しエラー ({model_choice}): {e}", exc_info=True)
            if retry < max_retries - 1:
                logger.info(f"API呼び出し: {retry + 1}回目のリトライ...")
                time.sleep(retry_delay)
                continue
            return f"API呼び出し中にエラー: {str(e)}"
    
    # すべてのリトライが失敗した場合
    return "APIサービスに接続できませんでした。後でもう一度お試しください。"

def get_episode_summary(episode_text: str, model_choice: str, max_length: int = 300) -> str:
    """
    エピソードテキストのサマリーを生成する
    
    Args:
        episode_text: 要約するエピソードのテキスト
        model_choice: 使用するAIモデル
        max_length: 要約の最大長さ
        
    Returns:
        str: エピソードのサマリー
    """
    # テキストが短い場合は要約せずにそのまま返す
    if len(episode_text) <= max_length:
        return episode_text
    
    # 要約プロンプト作成
    summary_prompt = f"""
以下の官能小説の内容を200字程度に要約してください。
物語の流れがわかるように重要な出来事とキャラクターの関係性を含めてください。

### 要約対象テキスト:
{episode_text}

### 指示:
- 200字程度で簡潔に要約すること
- 登場人物の名前と関係性を維持すること
- 物語の重要な転換点を含めること
- 官能描写は直接的な表現を避け「～という情事があった」など簡潔に示すこと
"""
    
    # API呼び出し
    try:
        summary = call_api_for_novel(model_choice, summary_prompt, max_tokens=400)
        logger.info(f"エピソード要約を生成しました: {len(summary)}文字")
        return summary
    except Exception as e:
        logger.error(f"要約生成エラー: {e}")
        # エラー時は元テキストの先頭部分を返す
        return episode_text[:max_length] + "..."