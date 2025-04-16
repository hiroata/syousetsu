// app.js - メインアプリケーションロジック

document.addEventListener('DOMContentLoaded', function() {
    // フォーム要素の取得
    const novelForm = document.getElementById('novelGenerationForm');
    const generateIdeasBtn = document.getElementById('generateIdeasBtn');
    const spinner = document.getElementById('spinner');
    const ideasContainer = document.getElementById('ideas-container');
    
    // 初期化処理
    initApp();
    
    // アプリケーションの初期化
    function initApp() {
        // 既存のストーリーがあるか確認し、あれば結果ページにリダイレクト
        const storyList = storyManager.getStoryList();
        if (storyList.length > 0) {
            redirectToResult();
        }
        
        // イベントリスナーの登録
        novelForm.addEventListener('submit', handleFormSubmit);
        generateIdeasBtn.addEventListener('click', handleGenerateIdeas);
    }
    
    // フォーム送信処理
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // 送信ボタンを無効化
        const submitBtn = novelForm.querySelector('.submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = '生成中...';
        
        try {
            // フォームデータの取得
            const formData = new FormData(novelForm);
            const formDataObj = {};
            
            // キャラクター情報の処理
            const characters = [];
            if (formData.get('character_name') && formData.get('character_name').trim()) {
                characters.push({
                    name: formData.get('character_name'),
                    description: formData.get('character_description')
                });
            }
            
            // フォームデータをオブジェクトに変換
            for (let [key, value] of formData.entries()) {
                if (key !== 'character_name' && key !== 'character_description') {
                    formDataObj[key] = value;
                }
            }
            
            // キャラクター情報の追加
            formDataObj.characters = characters;
            
            // APIリクエスト
            const response = await apiClient.generateStory(formDataObj);
            
            if (response.success) {
                // 成功した場合、ストーリーを保存して結果ページに遷移
                const episode = {
                    text: response.novel_text,
                    summary: response.summary,
                    title: response.title,
                    model: formDataObj.model_choice
                };
                
                // セッション情報も保存
                storyManager.saveSessionData({
                    prompt: formDataObj.prompt,
                    genre: formDataObj.genre,
                    instructions: formDataObj.instructions,
                    story_request: formDataObj.story_request,
                    font_choice: formDataObj.font_choice,
                    model_choice: formDataObj.model_choice,
                    characters: characters
                });
                
                // ストーリーの保存
                storyManager.addStoryEpisode(episode);
                
                // 結果ページにリダイレクト
                redirectToResult();
            } else {
                // エラーの場合
                alert('ストーリー生成中にエラーが発生しました: ' + response.error);
                submitBtn.disabled = false;
                submitBtn.textContent = '物語を生成';
            }
        } catch (error) {
            alert('エラーが発生しました: ' + error.message);
            submitBtn.disabled = false;
            submitBtn.textContent = '物語を生成';
        }
    }
    
    // アイデア生成処理
    async function handleGenerateIdeas() {
        const genre = document.getElementById('genre').value;
        const modelChoice = document.querySelector('input[name="model_choice"]:checked').value;
        
        // スピナー表示
        spinner.style.display = 'block';
        ideasContainer.style.display = 'none';
        
        try {
            // APIリクエスト
            const response = await apiClient.generateIdeas(genre, modelChoice);
            
            // スピナー非表示
            spinner.style.display = 'none';
            
            if (response.success) {
                // アイデアを表示
                ideasContainer.innerHTML = response.ideas.replace(/\n/g, '<br>');
                ideasContainer.style.display = 'block';
                
                // アイデアをクリックで入力欄に設定できるようにする
                const ideas = ideasContainer.innerHTML.split('<br><br>');
                ideasContainer.innerHTML = '';
                
                ideas.forEach((idea, index) => {
                    if (idea.trim() === '') return;
                    
                    const ideaDiv = document.createElement('div');
                    ideaDiv.className = 'idea-item';
                    ideaDiv.innerHTML = idea + '<br>';
                    
                    const selectButton = document.createElement('button');
                    selectButton.className = 'idea-select';
                    selectButton.textContent = 'このアイデアを使用';
                    selectButton.onclick = function() {
                        // 正規表現でプロット概要を抽出
                        const promptMatch = idea.match(/概要：(.*?)(?=登場人物|$)/s);
                        const charsMatch = idea.match(/登場人物：(.*?)(?=舞台|$)/s);
                        const settingMatch = idea.match(/舞台：(.*?)(?=$)/s);
                        
                        if (promptMatch) {
                            document.getElementById('prompt').value = promptMatch[1].trim();
                        }
                        
                        if (charsMatch) {
                            const chars = charsMatch[1].trim().split('、');
                            if (chars.length > 0 && chars[0]) {
                                document.getElementById('character_name').value = chars[0].split('：')[0] || '';
                                document.getElementById('character_description').value = chars[0].split('：')[1] || '';
                            }
                        }
                        
                        if (settingMatch) {
                            document.getElementById('instructions').value = '舞台：' + settingMatch[1].trim();
                        }
                    };
                    
                    ideaDiv.appendChild(selectButton);
                    ideasContainer.appendChild(ideaDiv);
                });
            } else {
                ideasContainer.innerHTML = 'アイデア生成中にエラーが発生しました: ' + response.error;
                ideasContainer.style.display = 'block';
            }
        } catch (error) {
            spinner.style.display = 'none';
            ideasContainer.innerHTML = 'エラー: ' + error.message;
            ideasContainer.style.display = 'block';
        }
    }
    
    // 結果ページへのリダイレクト
    function redirectToResult() {
        window.location.href = 'result.html';
    }
});