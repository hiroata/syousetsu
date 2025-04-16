import os
import aiohttp
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from config import Config

class AIService:
    """AIサービスの基本クラス"""
    
    # サポートするモデル一覧
    SUPPORTED_MODELS = ["xai", "grok-3", "gpt-4o", "claude-3-opus", "deepseek-v3"]
    
    @staticmethod
    async def generate_text(prompt: str, model_choice: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """モデル選択に基づいて適切なAPI呼び出しを行う"""
        try:
            # 非サポートモデルの場合はデフォルト（xAI）にフォールバック
            if model_choice not in AIService.SUPPORTED_MODELS:
                logging.warning(f"非サポートモデル '{model_choice}' が指定されました。xAIにフォールバックします。")
                model_choice = "xai"
            
            # モデル選択に基づいて適切なサービスを呼び出す
            if model_choice == "deepseek-v3":
                return await DeepseekService.generate_text(prompt, model_choice, max_tokens=max_tokens, temperature=temperature)
            elif model_choice == "claude-3-opus":
                return await AnthropicService.generate_text(prompt, model_choice, max_tokens=max_tokens, temperature=temperature)
            elif model_choice == "gpt-4o":
                return await OpenAIService.generate_text(prompt, model_choice, max_tokens=max_tokens, temperature=temperature)
            elif model_choice in ["xai", "grok-3"]:
                return await XAIService.generate_text(prompt, model_choice, max_tokens=max_tokens, temperature=temperature)
        except Exception as e:
            logging.error(f"テキスト生成エラー: {str(e)}")
            return f"エラーが発生しました: {str(e)}"

    @staticmethod
    def generate_text_sync(prompt: str, model_choice: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """非同期関数を同期的に呼び出すためのヘルパーメソッド"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    AIService.generate_text(prompt, model_choice, max_tokens, temperature),
                    loop
                )
                return future.result(timeout=300)  # 5分タイムアウト
            else:
                return asyncio.run(AIService.generate_text(prompt, model_choice, max_tokens, temperature))
        except Exception as e:
            logging.error(f"同期API呼び出しエラー: {str(e)}")
            return f"エラーが発生しました: {str(e)}"


class DeepseekService:
    """Deepseek API統合サービス"""
    
    API_BASE = Config.DEEPSEEK_API_BASE
    MODEL_NAME = "DeepSeek-V3-0324"
    
    @classmethod
    async def generate_text(cls, prompt: str, model_choice: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """DeepseekのAPIを使用してテキストを生成する"""
        # APIキーの確認
        if not Config.DEEPSEEK_API_KEY:
            raise ValueError("Deepseek APIキーが設定されていません。.envファイルを確認してください。")
        
        # リクエストヘッダー
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # リクエストボディ
        payload = {
            "model": cls.MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        logging.info(f"Deepseekリクエスト: model={cls.MODEL_NAME}, temp={temperature}, max_tokens={max_tokens}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{cls.API_BASE}/chat/completions", 
                    headers=headers, 
                    json=payload,
                    timeout=300
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_detail = await response.text()
                        raise Exception(f"Deepseek API error: {response.status} - {error_detail}")
        except Exception as e:
            logging.error(f"Deepseek API エラー: {str(e)}")
            raise


class AnthropicService:
    """Anthropic API統合サービス"""
    
    API_BASE = "https://api.anthropic.com/v1/messages"
    MODEL_NAME = "claude-3-opus-20240229"
    
    @classmethod
    async def generate_text(cls, prompt: str, model_choice: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """AnthropicのAPIを使用してテキストを生成する"""
        # APIキーの確認
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic APIキーが設定されていません。.envファイルを確認してください。")
        
        # リクエストヘッダー
        headers = {
            "x-api-key": Config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # リクエストボディ
        payload = {
            "model": cls.MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    cls.API_BASE, 
                    headers=headers, 
                    json=payload,
                    timeout=300
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["content"][0]["text"]
                    else:
                        error_detail = await response.text()
                        raise Exception(f"Anthropic API error: {response.status} - {error_detail}")
        except Exception as e:
            logging.error(f"Anthropic API エラー: {str(e)}")
            raise


class OpenAIService:
    """OpenAI API統合サービス"""
    
    API_BASE = "https://api.openai.com/v1/chat/completions"
    MODEL_NAME = "gpt-4o"
    
    @classmethod
    async def generate_text(cls, prompt: str, model_choice: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """OpenAIのAPIを使用してテキストを生成する"""
        # APIキーの確認
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI APIキーが設定されていません。.envファイルを確認してください。")
        
        # リクエストヘッダー
        headers = {
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # リクエストボディ
        payload = {
            "model": cls.MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    cls.API_BASE, 
                    headers=headers, 
                    json=payload,
                    timeout=300
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_detail = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_detail}")
        except Exception as e:
            logging.error(f"OpenAI API エラー: {str(e)}")
            raise


class XAIService:
    """xAI (Grok) API統合サービス"""
    
    API_BASE = "https://api.groq.com/openai/v1/chat/completions"
    MODEL_MAPPING = {
        "xai": "grok-2",
        "grok-3": "grok-3"
    }
    
    @classmethod
    async def generate_text(cls, prompt: str, model_choice: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """xAIのAPIを使用してテキストを生成する"""
        # モデル設定
        model_name = cls.MODEL_MAPPING.get(model_choice, "grok-2")
        
        # APIキーの確認
        if not Config.XAI_API_KEY:
            raise ValueError("xAI APIキーが設定されていません。.envファイルを確認してください。")
        
        # リクエストヘッダー
        headers = {
            "Authorization": f"Bearer {Config.XAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # リクエストボディ
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    cls.API_BASE, 
                    headers=headers, 
                    json=payload,
                    timeout=300
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_detail = await response.text()
                        raise Exception(f"xAI API error: {response.status} - {error_detail}")
        except Exception as e:
            logging.error(f"xAI API エラー: {str(e)}")
            raise