// location.js
document.addEventListener('DOMContentLoaded', function() {
    // 場所ギャラリーページの初期化
    if (document.getElementById('location-gallery')) {
        initGallery();
    }
    
    // 場所編集ページの初期化
    if (document.getElementById('location-edit-form')) {
        initEditForm();
    }
});

// ギャラリーページの初期化
function initGallery() {
    // 削除確認モーダルの設定
    const deleteButtons = document.querySelectorAll('.delete-location-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const locationId = this.getAttribute('data-id');
            const locationName = this.getAttribute('data-name');
            confirmDelete(locationId, locationName);
        });
    });
    
    // 場所使用ボタンの設定
    const useButtons = document.querySelectorAll('.use-location-btn');
    useButtons.forEach(button => {
        button.addEventListener('click', function() {
            const locationId = this.getAttribute('data-id');
            useLocation(locationId);
        });
    });
}

// 編集フォームの初期化
function initEditForm() {
    // カテゴリー選択変更時の処理
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            // カテゴリーに応じた特性・特徴の更新（必要に応じて）
        });
    }
    
    // ランダム生成ボタンの設定
    const randomButton = document.getElementById('generate-random-btn');
    if (randomButton) {
        randomButton.addEventListener('click', generateRandom);
    }
    
    // 個別フィールドのランダム生成ボタン設定
    const fieldButtons = document.querySelectorAll('.generate-field-btn');
    fieldButtons.forEach(button => {
        button.addEventListener('click', function() {
            const field = this.getAttribute('data-field');
            generateRandomField(field);
        });
    });
}

// 削除確認処理
function confirmDelete(locationId, locationName) {
    if (confirm(`「${locationName}」を削除しますか？この操作は元に戻せません。`)) {
        // 削除リクエストを送信
        fetch(`/locations/delete/${locationId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 成功時はページをリロード
                window.location.reload();
            } else {
                alert('削除に失敗しました：' + (data.error || '不明なエラー'));
            }
        })
        .catch(error => {
            console.error('Error deleting location:', error);
            alert('削除処理中にエラーが発生しました。');
        });
    }
}

// 場所を使用
function useLocation(locationId) {
    fetch(`/api/locations/${locationId}`)
        .then(response => response.json())
        .then(data => {
            // セッションストレージに保存
            sessionStorage.setItem('selected_location', JSON.stringify(data));
            // インデックスページに戻る
            window.location.href = '/?use_location=true';
        })
        .catch(error => {
            console.error('Error fetching location:', error);
            alert('場所情報の取得に失敗しました。');
        });
}

// 全体をランダム生成
function generateRandom() {
    fetch('/locations/generate_random', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        // カテゴリー設定
        if (data.category) {
            const categorySelect = document.getElementById('category');
            for (let i = 0; i < categorySelect.options.length; i++) {
                if (categorySelect.options[i].value === data.category) {
                    categorySelect.selectedIndex = i;
                    break;
                }
            }
        }
        
        // 各フィールドに値を設定
        document.getElementById('atmosphere').value = data.atmosphere || '';
        document.getElementById('features').value = data.features || '';
    })
    .catch(error => {
        console.error('Error generating random location:', error);
        alert('ランダム生成中にエラーが発生しました。');
    });
}

// 特定フィールドのみランダム生成
function generateRandomField(field) {
    fetch('/locations/generate_random', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        // 指定されたフィールドのみ更新
        if (data[field]) {
            document.getElementById(field).value = data[field];
        }
    })
    .catch(error => {
        console.error('Error generating random field:', error);
        alert('ランダム生成中にエラーが発生しました。');
    });
}