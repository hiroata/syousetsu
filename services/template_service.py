cat > app/services/template_service.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Template service for the novel generator application.
Handles templates for various uses in the novel generation process.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

# ロギングの設定
logger = logging.getLogger('novel_generator')

def load_templates() -> List[Dict[str, Any]]:
    """
    プロンプトテンプレート一覧を読み込む
    
    Returns:
        List[Dict[str, Any]]: テンプレートのリスト
    """
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'templates.json')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"テンプレート読み込みエラー: {e}")
        return []

def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """
    IDを指定してテンプレートを取得
    
    Args:
        template_id: テンプレートのID
        
    Returns:
        Optional[Dict[str, Any]]: テンプレート情報
    """
    templates = load_templates()
    for template in templates:
        if template.get('id') == template_id:
            return template
    return None

def save_template(template: Dict[str, Any]) -> bool:
    """
    テンプレートを保存する
    
    Args:
        template: 保存するテンプレート情報
        
    Returns:
        bool: 保存成功かどうか
    """
    try:
        templates = load_templates()
        
        # IDがある場合は更新、ない場合は新規追加
        if 'id' in template:
            for i, t in enumerate(templates):
                if t.get('id') == template['id']:
                    templates[i] = template
                    break
            else:
                templates.append(template)
        else:
            # 新規IDを生成
            max_id = 0
            for t in templates:
                if 'id' in t and t['id'].isdigit():
                    max_id = max(max_id, int(t['id']))
            template['id'] = str(max_id + 1)
            templates.append(template)
        
        # 保存
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'templates.json')
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"テンプレート保存エラー: {e}")
        return False

def delete_template(template_id: str) -> bool:
    """
    テンプレートを削除する
    
    Args:
        template_id: 削除するテンプレートのID
        
    Returns:
        bool: 削除成功かどうか
    """
    try:
        templates = load_templates()
        templates = [t for t in templates if t.get('id') != template_id]
        
        # 保存
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'templates.json')
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"テンプレート削除エラー: {e}")
        return False

def get_template_categories() -> List[str]:
    """
    テンプレートのカテゴリ一覧を取得
    
    Returns:
        List[str]: カテゴリのリスト
    """
    templates = load_templates()
    categories = set()
    for template in templates:
        if 'category' in template:
            categories.add(template['category'])
    return sorted(list(categories))

def get_templates_by_category(category: str) -> List[Dict[str, Any]]:
    """
    カテゴリでテンプレートをフィルタリング
    
    Args:
        category: フィルタリングするカテゴリ
        
    Returns:
        List[Dict[str, Any]]: テンプレートのリスト
    """
    templates = load_templates()
    return [t for t in templates if t.get('category') == category]
EOF