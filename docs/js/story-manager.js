// story-manager.js - ストーリーとセッションの管理

class StoryManager {
    constructor() {
      this.storyListKey = 'novel_story_list'; // ストーリーリストのストレージキー
      this.sessionDataKey = 'novel_session_data'; // セッションデータのストレージキー
    }
  
    /**
     * ストーリーリストを取得
     * @returns {Array} ストーリーエピソードの配列
     */
    getStoryList() {
      const storedData = localStorage.getItem(this.storyListKey);
      return storedData ? JSON.parse(storedData) : [];
    }
  
    /**
     * ストーリーリストを保存
     * @param {Array} storyList - ストーリーエピソードの配列
     */
    saveStoryList(storyList) {
      localStorage.setItem(this.storyListKey, JSON.stringify(storyList));
    }
  
    /**
     * 新しいエピソードをストーリーに追加
     * @param {Object} episode - 追加するエピソード
     * @returns {Array} 更新されたストーリーリスト
     */
    addStoryEpisode(episode) {
      const storyList = this.getStoryList();
      storyList.push(episode);
      this.saveStoryList(storyList);
      return storyList;
    }
  
    /**
     * セッションデータを取得
     * @returns {Object} セッションデータ
     */
    getSessionData() {
      const storedData = localStorage.getItem(this.sessionDataKey);
      return storedData ? JSON.parse(storedData) : {};
    }
  
    /**
     * セッションデータを保存
     * @param {Object} sessionData - 保存するセッションデータ
     */
    saveSessionData(sessionData) {
      localStorage.setItem(this.sessionDataKey, JSON.stringify(sessionData));
    }
  
    /**
     * 最新エピソードの情報を取得
     * @returns {Object} 最新エピソードのコンテキスト情報
     */
    getLatestEpisodeContext() {
      const storyList = this.getStoryList();
      const sessionData = this.getSessionData();
      
      if (storyList.length === 0) {
        return null;
      }
      
      const latestEpisode = storyList[storyList.length - 1];
      
      return {
        summary: latestEpisode.summary,
        episode_number: storyList.length,
        title: latestEpisode.title,
        model: latestEpisode.model,
        genre: sessionData.genre,
        prompt: sessionData.prompt,
        characters: sessionData.characters || []
      };
    }
  
    /**
     * すべてのデータをクリア
     */
    clearAllData() {
      localStorage.removeItem(this.storyListKey);
      localStorage.removeItem(this.sessionDataKey);
    }
  
    /**
     * ストーリーをエクスポート（ダウンロード用）
     * @returns {Object} エクスポート用のデータ
     */
    exportStory() {
      return {
        storyList: this.getStoryList(),
        sessionData: this.getSessionData(),
        exportDate: new Date().toISOString()
      };
    }
  
    /**
     * ストーリーをインポート
     * @param {Object} importData - インポートするデータ
     * @returns {boolean} インポートの成否
     */
    importStory(importData) {
      try {
        if (!importData || !importData.storyList || !Array.isArray(importData.storyList)) {
          return false;
        }
        
        this.saveStoryList(importData.storyList);
        
        if (importData.sessionData) {
          this.saveSessionData(importData.sessionData);
        }
        
        return true;
      } catch (error) {
        console.error('インポート中にエラーが発生しました:', error);
        return false;
      }
    }
  }
  
  // グローバルインスタンスの作成
  const storyManager = new StoryManager();