#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Character-related routes for the novel generator application.
Handles character creation, editing, and management.
"""

import os
import json
import re
import datetime
import logging
import random
from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify, flash, current_app
from bson.objectid import ObjectId

# utils からインポート
from utils.text_utils import generate_random_character_legacy, tags_string_to_list, tags_list_to_string, get_character_kinks_by_gender
from models.character import Character

# ロギングの設定
logger = logging.getLogger('novel_generator')

# Blueprint 定義
character_bp = Blueprint('character', __name__)

########################################
# キャラクター一覧表示: /characters
########################################
@character_bp.route('/characters')
def list_characters():
    try:
        # データベースからキャラクター一覧を取得
        characters = Character.find_all()
        return render_template('characters/index.html', characters=characters)
    except Exception as e:
        logger.error(f"キャラクター一覧取得エラー: {e}", exc_info=True)
        flash('キャラクター一覧の取得中にエラーが発生しました。', 'danger')
        return redirect(url_for('novel.home'))

########################################
# キャラクター作成画面: /characters/create
########################################
@character_bp.route('/characters/create')
def create_character():
    try:
        # 性別ごとの性癖リストを取得
        male_kinks_dict = get_character_kinks_by_gender('male')
        female_kinks_dict = get_character_kinks_by_gender('female')
        
        # 上位15件をサンプル表示用に抽出（実際にはJSで全件取得される）
        male_kinks_sample = list(male_kinks_dict.keys())[:15]
        female_kinks_sample = list(female_kinks_dict.keys())[:15]
        
        return render_template('characters/edit.html', 
                              character={},
                              is_new=True,
                              male_kinks_sample=male_kinks_sample,
                              female_kinks_sample=female_kinks_sample)
    except Exception as e:
        logger.error(f"キャラクター作成画面表示エラー: {e}", exc_info=True)
        flash('キャラクター作成画面の表示中にエラーが発生しました。', 'danger')
        return redirect(url_for('character.list_characters'))

########################################
# キャラクター編集画面: /characters/edit/<character_id>
########################################
@character_bp.route('/characters/edit/<character_id>')
def edit_character(character_id):
    try:
        # データベースからキャラクター情報を取得
        character = Character.find_by_id(character_id)
        if not character:
            flash('キャラクターが見つかりませんでした。', 'warning')
            return redirect(url_for('character.list_characters'))
        
        # 性別ごとの性癖リストを取得
        male_kinks_dict = get_character_kinks_by_gender('male')
        female_kinks_dict = get_character_kinks_by_gender('female')
        
        # 上位15件をサンプル表示用に抽出（実際にはJSで全件取得される）
        male_kinks_sample = list(male_kinks_dict.keys())[:15]
        female_kinks_sample = list(female_kinks_dict.keys())[:15]
        
        return render_template('characters/edit.html', 
                              character=character,
                              is_new=False,
                              male_kinks_sample=male_kinks_sample,
                              female_kinks_sample=female_kinks_sample)
    except Exception as e:
        logger.error(f"キャラクター編集画面表示エラー: {e}", exc_info=True)
        flash('キャラクター編集画面の表示中にエラーが発生しました。', 'danger')
        return redirect(url_for('character.list_characters'))

########################################
# キャラクター保存: /characters/save
########################################
@character_bp.route('/characters/save', methods=['POST'])
def save_character():
    try:
        # フォームからデータを取得
        character_data = {
            'name': request.form.get('name', '').strip(),
            'gender': request.form.get('gender', 'male'),
            'age': request.form.get('age', '').strip(),
            'occupation': request.form.get('occupation', '').strip(),
            'appearance': request.form.get('appearance', '').strip(),
            'personality': request.form.get('personality', '').strip(),
            'speech_pattern': request.form.get('speech_pattern', '').strip(),
            'kinks': request.form.get('kinks', '').strip(),
            'tags': request.form.get('tags', '').strip(),
            'updated_at': datetime.datetime.now()
        }
        
        # 新規作成か更新かを判定
        character_id = request.form.get('id')
        
        if character_id:  # 更新
            # データベースのキャラクター情報を更新
            character = Character.update(character_id, character_data)
            if character:
                flash('キャラクターを更新しました。', 'success')
            else:
                flash('キャラクターの更新に失敗しました。', 'danger')
        else:  # 新規作成
            character_data['created_at'] = datetime.datetime.now()
            # データベースに新規キャラクターを作成
            character = Character.create(character_data)
            if character:
                flash('新しいキャラクターを作成しました。', 'success')
            else:
                flash('キャラクターの作成に失敗しました。', 'danger')
        
        return redirect(url_for('character.list_characters'))
    except Exception as e:
        logger.error(f"キャラクター保存エラー: {e}", exc_info=True)
        flash('キャラクターの保存中にエラーが発生しました。', 'danger')
        return redirect(url_for('character.list_characters'))

########################################
# キャラクター削除: /characters/delete/<character_id>
########################################
@character_bp.route('/characters/delete/<character_id>', methods=['POST'])
def delete_character(character_id):
    try:
        # データベースからキャラクターを削除
        result = Character.delete(character_id)
        
        # AJAX リクエストの場合はJSONレスポンスを返す
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if result:
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'キャラクターの削除に失敗しました。'})
        
        # 通常のリクエストの場合はリダイレクト
        if result:
            flash('キャラクターを削除しました。', 'success')
        else:
            flash('キャラクターの削除に失敗しました。', 'danger')
            
        return redirect(url_for('character.list_characters'))
    except Exception as e:
        logger.error(f"キャラクター削除エラー: {e}", exc_info=True)
        
        # AJAX リクエストの場合はJSONレスポンスを返す
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)})
            
        flash('キャラクターの削除中にエラーが発生しました。', 'danger')
        return redirect(url_for('character.list_characters'))

########################################
# キャラクターランダム生成API: /characters/generate_random
########################################
@character_bp.route('/characters/generate_random', methods=['POST'])
def generate_random():
    try:
        data = request.get_json() or {}
        gender = data.get('gender', 'male')
        
        # 性癖辞書を取得
        kinks_dict = get_character_kinks_by_gender(gender)
        
        # ランダムに2〜4つの性癖を選択
        num_kinks = random.randint(2, 4)
        selected_kinks = random.sample(list(kinks_dict.keys()), min(num_kinks, len(kinks_dict)))
        kinks_str = "、".join(selected_kinks)
        
        # キャラクター生成
        name, description = generate_random_character_legacy(gender, kinks_str)
        
        # 生成されたデータからパース
        age_match = re.search(r'(\d+)歳', description)
        age = age_match.group(1) if age_match else random.randint(22, 45)
        
        occupation_match = re.search(r'は(.+?)。', description)
        occupation = occupation_match.group(1) if occupation_match else ""
        
        appearance_match = re.search(r'。(.+?)で、', description)
        appearance = appearance_match.group(1) if appearance_match else ""
        
        personality_match = re.search(r'性格は(.+?)。', description)
        personality = personality_match.group(1) if personality_match else ""
        
        # レスポンスデータ作成
        character_data = {
            'name': name,
            'gender': gender,
            'age': age,
            'occupation': occupation,
            'appearance': appearance,
            'personality': personality,
            'speech_pattern': "",  # 話し方は空欄
            'kinks': kinks_str
        }
        
        return jsonify(character_data)
    except Exception as e:
        logger.error(f"キャラクターランダム生成エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# キャラクター情報取得API: /api/characters/<character_id>
########################################
@character_bp.route('/api/characters/<character_id>')
def get_character_api(character_id):
    try:
        # データベースからキャラクター情報を取得
        character = Character.find_by_id(character_id)
        if not character:
            return jsonify({'error': 'キャラクターが見つかりません'}), 404
            
        return jsonify(character)
    except Exception as e:
        logger.error(f"キャラクター情報取得API エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# キャラクター一覧取得API: /api/characters
########################################
@character_bp.route('/api/characters')
def get_characters_api():
    try:
        # データベースからキャラクター一覧を取得
        characters = Character.find_all()
        return jsonify(characters)
    except Exception as e:
        logger.error(f"キャラクター一覧取得API エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# 性別に応じた性癖リスト取得API: /api/character_kinks/<gender>
########################################
@character_bp.route('/api/character_kinks/<gender>')
def get_character_kinks_api(gender):
    try:
        # 性別に応じた性癖リスト取得
        kinks_dict = get_character_kinks_by_gender(gender)
        
        # 辞書のキーのリストを返す
        return jsonify(list(kinks_dict.keys()))
    except Exception as e:
        logger.error(f"性癖リスト取得API エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500