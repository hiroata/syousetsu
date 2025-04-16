// character.js
document.addEventListener('DOMContentLoaded', function() {
    // キャラクターギャラリーページの初期化
    if (document.getElementById('character-gallery')) {
        initGallery();
    }
    
    // キャラクター編集ページの初期化
    if (document.getElementById('character-edit-form')) {
        initEditForm();
    }
});

// ギャラリーページの初期化
function initGallery() {
    // 削除確認モーダルの設定
    const deleteButtons = document.querySelectorAll('.delete-character-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const characterId = this.getAttribute('data-id');
            const characterName = this.getAttribute('data-name');
            confirmDelete(characterId, characterName);
        });
    });
    
    // キャラクター使用ボタンの設定
    const useButtons = document.querySelectorAll('.use-character-btn');
    useButtons.forEach(button => {
        button.addEventListener('click', function() {
            const characterId = this.getAttribute('data-id');
            useCharacter(characterId);
        });
    });
}

// 編集フォームの初期化
function initEditForm() {
    // 性別選択変更時の処理
    const genderSelect = document.getElementById('gender');
    if (genderSelect) {
        genderSelect.addEventListener('change', function() {
            // 性別に応じた特性・特徴の更新（必要に応じて）
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
function confirmDelete(characterId, characterName) {
    if (confirm(`「${characterName}」を削除しますか？この操作は元に戻せません。`)) {
        // 削除リクエストを送信
        fetch(`/characters/delete/${characterId}`, {
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
            console.error('Error deleting character:', error);
            alert('削除処理中にエラーが発生しました。');
        });
    }
}

// キャラクターを使用
function useCharacter(characterId) {
    fetch(`/api/characters/${characterId}`)
        .then(response => response.json())
        .then(data => {
            // セッションストレージに保存
            sessionStorage.setItem('selected_character', JSON.stringify(data));
            // インデックスページに戻る
            window.location.href = '/?use_character=true';
        })
        .catch(error => {
            console.error('Error fetching character:', error);
            alert('キャラクター情報の取得に失敗しました。');
        });
}

// 全体をランダム生成
function generateRandom() {
    const gender = document.getElementById('gender').value;
    
    fetch('/characters/generate_random', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gender: gender })
    })
    .then(response => response.json())
    .then(data => {
        // 各フィールドに値を設定
        document.getElementById('occupation').value = data.occupation || '';
        document.getElementById('age').value = data.age || '';
        document.getElementById('appearance').value = data.appearance || '';
        document.getElementById('personality').value = data.personality || '';
        document.getElementById('speech_pattern').value = data.speech_pattern || '';
        document.getElementById('kinks').value = data.kinks || '';
    })
    .catch(error => {
        console.error('Error generating random character:', error);
        alert('ランダム生成中にエラーが発生しました。');
    });
}

// 特定フィールドのみランダム生成
function generateRandomField(field) {
    const gender = document.getElementById('gender').value;
    
    fetch('/characters/generate_random', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gender: gender })
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