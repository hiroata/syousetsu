#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Location routes for the novel generator application.
Handles all location-related functionality.
"""

import os
import logging
from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash, current_app
from models import db, Location
from utils import generate_random_location

# ロギングの設定
logger = logging.getLogger('novel_generator')

# Blueprint definition
location_bp = Blueprint('location', __name__)

########################################
# 場所ギャラリー: /locations
########################################
@location_bp.route('/locations')
def gallery():
    """場所ギャラリーを表示"""
    try:
        # すべての場所を取得
        locations = Location.get_all_json()
        return render_template('location/gallery.html', locations=locations)
    except Exception as e:
        logger.error(f"場所ギャラリー表示エラー: {e}", exc_info=True)
        return render_template('error.html', 
                              error_title='場所ギャラリーエラー',
                              error_message=f'場所の読み込み中にエラーが発生しました: {str(e)}',
                              back_link='/')

########################################
# 場所作成: /locations/create
########################################
@location_bp.route('/locations/create')
def create():
    """新規場所作成画面を表示"""
    try:
        # 空の場所設定を表示
        location_settings = generate_random_location()
        return render_template('location/edit.html', 
                              location=location_settings, 
                              title="新規場所作成",
                              is_new=True)
    except Exception as e:
        logger.error(f"場所作成画面表示エラー: {e}", exc_info=True)
        return render_template('error.html', 
                              error_title='場所作成エラー',
                              error_message=f'場所作成画面の表示中にエラーが発生しました: {str(e)}',
                              back_link='/locations')

########################################
# 場所編集: /locations/edit/<location_id>
########################################
@location_bp.route('/locations/edit/<int:location_id>')
def edit(location_id):
    """場所編集画面を表示"""
    try:
        # 場所を取得
        location = Location.query.get_or_404(location_id)
        return render_template('location/edit.html', 
                              location=location.to_dict(), 
                              title=f"{location.name} の編集",
                              is_new=False)
    except Exception as e:
        logger.error(f"場所編集画面表示エラー (ID: {location_id}): {e}", exc_info=True)
        return render_template('error.html', 
                              error_title='場所編集エラー',
                              error_message=f'場所編集画面の表示中にエラーが発生しました: {str(e)}',
                              back_link='/locations')

########################################
# 場所保存: /locations/save
########################################
@location_bp.route('/locations/save', methods=['POST'])
def save():
    """場所情報を保存"""
    try:
        # フォームからデータを取得
        location_id = request.form.get('id', type=int)
        
        # IDがある場合は既存の場所を取得、なければ新規作成
        if location_id:
            location = Location.query.get_or_404(location_id)
        else:
            location = Location()
        
        # 場所情報更新
        location.name = request.form.get('name', '')
        location.category = request.form.get('category', '')
        location.description = request.form.get('description', '')
        location.atmosphere = request.form.get('atmosphere', '')
        location.features = request.form.get('features', '')
        location.tags = request.form.get('tags', '')
        
        # DB保存
        db.session.add(location)
        db.session.commit()
        
        # JSONファイルにも保存
        location.save_to_json()
        
        # 保存成功メッセージをフラッシュ
        flash('場所情報を保存しました', 'success')
        
        # ギャラリーページにリダイレクト
        return redirect(url_for('location.gallery'))
    except Exception as e:
        logger.error(f"場所保存エラー: {e}", exc_info=True)
        # ロールバック
        db.session.rollback()
        return render_template('error.html', 
                              error_title='場所保存エラー',
                              error_message=f'場所情報の保存中にエラーが発生しました: {str(e)}',
                              back_link='/locations')

########################################
# 場所削除: /locations/delete/<location_id>
########################################
@location_bp.route('/locations/delete/<int:location_id>', methods=['POST'])
def delete(location_id):
    """場所を削除"""
    try:
        # 場所を取得
        location = Location.query.get_or_404(location_id)
        
        # JSONファイルを削除
        filename = f"{location.id}_{location.name.replace(' ', '_')}.json"
        filepath = os.path.join(current_app.config['LOCATION_DIR'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # DBから削除
        db.session.delete(location)
        db.session.commit()
        
        # 削除成功メッセージをフラッシュ
        flash('場所を削除しました', 'success')
        
        # APIの場合はJSON応答
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        
        # 通常はギャラリーページにリダイレクト
        return redirect(url_for('location.gallery'))
    except Exception as e:
        logger.error(f"場所削除エラー (ID: {location_id}): {e}", exc_info=True)
        # ロールバック
        db.session.rollback()
        
        # APIの場合はJSONエラー応答
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
        
        return render_template('error.html', 
                              error_title='場所削除エラー',
                              error_message=f'場所の削除中にエラーが発生しました: {str(e)}',
                              back_link='/locations')

########################################
# 場所ランダム生成: /locations/generate_random
########################################
@location_bp.route('/locations/generate_random', methods=['POST'])
def generate_random():
    """ランダムな場所設定を生成"""
    try:
        random_location = generate_random_location()
        return jsonify(random_location)
    except Exception as e:
        logger.error(f"場所ランダム生成エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# APIリソース: /api/locations/<location_id>
########################################
@location_bp.route('/api/locations/<int:location_id>')
def api_get(location_id):
    """APIで特定の場所情報を返す"""
    try:
        location = Location.query.get_or_404(location_id)
        return jsonify({
            'id': location.id,
            'name': location.name,
            'category': location.category,
            'description': location.description,
            'atmosphere': location.atmosphere,
            'features': location.features,
            'tags': location.tags,
            'full_description': location.get_description()
        })
    except Exception as e:
        logger.error(f"API 場所取得エラー (ID: {location_id}): {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

########################################
# APIリソース: /api/locations
########################################
@location_bp.route('/api/locations')
def api_list():
    """APIで場所一覧を返す"""
    try:
        locations = Location.query.all()
        result = []
        for location in locations:
            result.append({
                'id': location.id,
                'name': location.name,
                'category': location.category,
                'description': location.get_description()
            })
        return jsonify(result)
    except Exception as e:
        logger.error(f"API 場所一覧エラー: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500