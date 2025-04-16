// result.js - 結果表示ページのロジック

document.addEventListener('DOMContentLoaded', function() {
    // 要素の取得
    const episodeTitle = document.getElementById('episode-title');
    const modelBadge = document.getElementById('model-badge');
    const novelContent = document.getElementById('novel-content');
    const continueButton = document.getElementById('continue-button');
    const episodeList = document.getElementById('episode-list');
    const loadingModal = document.getElementById('loading-modal');
    
    // 結果ページの初期化
    initResultPage();
    
    // 結果ページの初期化
    function initResultPage() {
        // ストーリーデータをローカルストレージから取得
        const storyList = storyManager.getStoryList();
        const sessionData = storyManager.getSessionData();
        
        // ストーリーがない場合はトップページにリダイレクト
        if (!storyList || storyList.length === 0) {
            window.location.href = 'index.html';
            return;
        }
        
        // 現在のエピソードを表示
        showCurrentEpisode(storyList, sessionData);
        
        // エピソードリストを表示
        updateEpisodeList(storyList);
        
        // 続き生成ボタンのイベント設定
        continueButton.addEventListener('click', handleContinueStory);
    }
    
    // 現在のエピソードを表示
    function showCurrentEpisode(storyList, sessionData) {
        const currentEpisode = storyList[storyList.length - 1];
        
        // エピソードタイトルの設定
        episodeTitle.innerHTML = currentEpisode.title;
        
        // モデルバッジの設定
        modelBadge.className = `model-badge ${currentEpisode.model}`;
        switch (currentEpisode.model) {
            case 'xai':
                modelBadge.textContent = 'Grok-3';
                break;
            case 'gemini':
                modelBadge.textContent = 'Gemini 2.5';
                break;
            case 'anthropic':
                modelBadge.textContent = 'Claude 3.5';
                break;
            case 'openai':
                modelBadge.textContent = 'GPT-4';
                break;
            default:
                modelBadge.textContent = currentEpisode.model;
        }
        
        // 小説テキストの設定（Markdownをレンダリング）
        novelContent.innerHTML = marked.parse(currentEpisode.text);
        
        // フォントスタイルの適用
        if (sessionData.font_choice === 'serif') {
            document.body.classList.add('serif-font');
        } else {
            document.body.classList.remove('serif-font');
        }
    }
    
    // エピソードリストの更新
    function updateEpisodeList(storyList) {
        // リストをクリア
        episodeList.innerHTML = '';
        
        // 各エピソードをリストに追加
        storyList.forEach((episode, index) => {
            const listItem = document.createElement('li');
            
            // 現在のエピソードにはクラスを追加
            if (index === storyList.length - 1) {
                listItem.className = 'current-episode';
            }
            
            // エピソードリンクの作成
            const episodeLink = document.createElement('a');
            episodeLink.href = '#';
            episodeLink.textContent = `${episode.title}: ${episode.summary}`;
            
            // モデルバッジの作成
            const badgeSpan = document.createElement('span');
            badgeSpan.className = `model-badge ${episode.model}`;
            
            switch (episode.model) {
                case 'xai':
                    badgeSpan.textContent = 'Grok-3';
                    break;
                case 'gemini':
                    badgeSpan.textContent = 'Gemini 2.5';
                    break;
                case 'anthropic':
                    badgeSpan.textContent = 'Claude 3.5';
                    break;
                case 'openai':
                    badgeSpan.textContent = 'GPT-4';
                    break;
                default:
                    badgeSpan.textContent = episode.model;
            }
            
            // クリックイベントの追加
            episodeLink.addEventListener('click', function(e) {
                e.preventDefault();
                showEpisode(index);
            });
            
            // 要素の追加
            episodeLink.appendChild(badgeSpan);
            listItem.appendChild(episodeLink);
            episodeList.appendChild(listItem);
        });
    }
    
    // 指定されたエピソードを表示
    function showEpisode(index) {
        const storyList = storyManager.getStoryList();
        const sessionData = storyManager.getSessionData();
        
        if (index >= 0 && index < storyList.length) {
            // 指定されたエピソードをカレントに設定して表示
            const tempStoryList = [...storyList];
            const selectedEpisode = tempStoryList[index];
            
            // 表示のためだけに最後のエピソードとして扱う
            episodeTitle.innerHTML = selectedEpisode.title;
            
            // モデルバッジの設定
            modelBadge.className = `model-badge ${selectedEpisode.model}`;
            switch (selectedEpisode.model) {
                case 'xai':
                    modelBadge.textContent = 'Grok-3';
                    break;
                case 'gemini':
                    modelBadge.textContent = 'Gemini 2.5';
                    break;
                case 'anthropic':
                    modelBadge.textContent = 'Claude 3.5';
                    break;
                case 'openai':
                    modelBadge.textContent = 'GPT-4';
                    break;
                default:
                    modelBadge.textContent = selectedEpisode.model;
            }
            
            // テキストの設定
            novelContent.innerHTML = marked.parse(selectedEpisode.text);
            
            // エピソードリストの更新（選択状態の反映）
            const listItems = episodeList.querySelectorAll('li');
            listItems.forEach((item, i) => {
                if (i === index) {
                    item.classList.add('current-episode');
                } else {
                    item.classList.remove('current-episode');
                }
            });
            
            // 続き生成ボタンの有効性
            if (index === storyList.length - 1) {
                continueButton.style.display = 'inline-block';
            } else {
                continueButton.style.display = 'none';
            }
        }
    }
    
    // 続き生成の処理
    async function handleContinueStory() {
        const storyList = storyManager.getStoryList();
        const sessionData = storyManager.getSessionData();
        
        if (!storyList || storyList.length === 0) {
            alert('ストーリーデータがありません。');
            return;
        }
        
        // ローディングモーダルの表示
        loadingModal.style.display = 'flex';
        
        // 続き生成に必要なデータの準備
        const previousSummary = storyList[storyList.length - 1].summary;
        const episodeNumber = storyList.length + 1;
        
        try {
            // APIリクエスト
            const response = await apiClient.continueStory({
                prompt: sessionData.prompt,
                genre: sessionData.genre,
                instructions: sessionData.instructions,
                story_request: sessionData.story_request,
                model_choice: sessionData.model_choice,
                previous_summary: previousSummary,
                episode_number: episodeNumber,
                characters: sessionData.characters || []
            });
            
            // ローディングモーダルを非表示
            loadingModal.style.display = 'none';
            
            if (response.success) {
                // 新しいエピソードの保存
                const newEpisode = {
                    text: response.novel_text,
                    summary: response.summary,
                    title: response.title,
                    model: sessionData.model_choice
                };
                
                // ストーリーに追加
                storyManager.addStoryEpisode(newEpisode);
                
                // 画面の更新
                const updatedStoryList = storyManager.getStoryList();
                showCurrentEpisode(updatedStoryList, sessionData);
                updateEpisodeList(updatedStoryList);
            } else {
                alert('続き生成中にエラーが発生しました: ' + response.error);
            }
        } catch (error) {
            loadingModal.style.display = 'none';
            alert('エラーが発生しました: ' + error.message);
        }
    }
});