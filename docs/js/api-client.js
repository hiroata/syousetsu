// api-client.js - バックエンドAPIとの通信を処理

class AINovelAPI {
    /**
     * APIクライアントの初期化
     * @param {string} baseUrl - APIサーバーのベースURL
     */
    constructor(baseUrl) {
      // 本番環境のAPIサーバーURLを設定（デプロイ後に変更）
      this.baseUrl = baseUrl || 'https://your-api-server.onrender.com';
      
      // 開発環境の場合はローカルURLを使用
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        this.baseUrl = 'http://localhost:5000';
      }
    }
  
    /**
     * APIリクエストを送信する汎用メソッド
     * @param {string} endpoint - APIエンドポイント
     * @param {Object} data - リクエストデータ
     * @returns {Promise<Object>} レスポンスデータ
     */
    async sendRequest(endpoint, data) {
      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
        
        const responseData = await response.json();
        
        // エラーレスポンスの処理
        if (!response.ok) {
          throw new Error(responseData.error || `APIエラー: ${response.status}`);
        }
        
        return responseData;
      } catch (error) {
        console.error(`API通信エラー (${endpoint}):`, error);
        return {
          success: false,
          error: error.message || 'APIリクエスト中に不明なエラーが発生しました'
        };
      }
    }
  
    /**
     * アイデア生成API
     * @param {string} genre - 小説のジャンル
     * @param {string} modelChoice - 使用するAIモデル
     * @returns {Promise<Object>} 生成されたアイデア
     */
    async generateIdeas(genre, modelChoice) {
      return this.sendRequest('/api/ideas', { 
        genre, 
        model_choice: modelChoice 
      });
    }
  
    /**
     * 小説生成API
     * @param {Object} storyData - 小説生成に必要なデータ
     * @returns {Promise<Object>} 生成された小説データ
     */
    async generateStory(storyData) {
      return this.sendRequest('/api/generate', storyData);
    }
  
    /**
     * 小説の続き生成API
     * @param {Object} storyContext - 続き生成に必要なコンテキスト
     * @returns {Promise<Object>} 生成された続きデータ
     */
    async continueStory(storyContext) {
      return this.sendRequest('/api/continue', storyContext);
    }
  
    /**
     * モックAPIレスポンス（開発用）
     * @param {string} type - レスポンスタイプ
     * @returns {Promise<Object>} モックデータ
     */
    async getMockResponse(type) {
      // URLのクエリパラメータにdebug=trueがある場合にのみモックを使用
      const urlParams = new URLSearchParams(window.location.search);
      const debugMode = urlParams.get('debug') === 'true';
      
      if (!debugMode) {
        throw new Error('モックモードが有効ではありません');
      }
      
      // モックデータを返す（開発・テスト用）
      switch (type) {
        case 'ideas':
          return {
            success: true,
            ideas: `アイデア1:\n概要：魔法学校で特殊な能力を持つ少年の成長物語\n登場人物：山田太郎：15歳、特殊な魔法の才能を持つ\n舞台：魔法が日常的に使われる異世界の学園\n\nアイデア2:\n概要：記憶を失った少女が自分の過去を探る冒険\n登場人物：佐藤花子：記憶喪失の17歳少女\n舞台：記憶を管理する組織が存在する近未来都市\n\nアイデア3:\n概要：古い洋館に住む不思議な老人と訪れた少年の交流\n登場人物：鈴木次郎：好奇心旺盛な12歳の少年\n舞台：山奥の古い洋館と周辺の森`
          };
        
        case 'generate':
          return {
            success: true,
            novel_text: `　山田太郎は窓際の席に座り、教室の外を見つめていた。魔法学園「星風学園」の入学式から一週間が経ち、ようやく授業にも慣れてきたところだった。しかし彼の心には常に不安があった。他の生徒たちは、入学前から基礎的な魔法を習得しているのに対し、太郎は魔法の才能に目覚めたのがつい最近だったからだ。\n\n　「次の実技試験、どうしよう...」\n\n　太郎はため息をつきながら呟いた。明日は初めての実技試験があり、基本的な火の魔法を披露しなければならない。彼は何度も練習したが、うまく火を灯すことができなかった。\n\n　「大丈夫？なんだか元気ないね」\n\n　突然、後ろから声をかけられ太郎は振り向いた。そこには、クラスメイトの佐藤美咲が立っていた。彼女は入学してすぐに評判になった天才少女で、どんな魔法も難なくこなすと言われていた。\n\n　「ああ、ちょっと明日の実技試験のことを考えてて...」\n\n　「練習手伝おうか？私、火の魔法得意だよ」\n\n　美咲は満面の笑みで言った。太郎は驚いたが、ありがたく申し出を受けることにした。\n\n　放課後、二人は空き教室に残り特訓を始めた。美咲は太郎の魔法の使い方を見て、すぐに問題点を指摘した。\n\n　「太郎君、魔力の流れが不安定だよ。もっと呼吸を整えて、ゆっくり集中して」\n\n　美咲のアドバイスに従い、太郎は深呼吸をして魔力を手のひらに集中させた。すると、今までにない感覚が体を駆け巡った。そして、手のひらから小さな火の玉が生まれた。\n\n　「やった！できた！」\n\n　太郎は喜びのあまり叫んだ。火の玉はすぐに消えてしまったが、確かに魔法を使えたのだ。\n\n　「すごい！才能あるよ、太郎君。きっと明日も大丈夫」\n\n　美咲が笑顔で言うと、太郎の心に温かいものが広がった。魔法学園での新しい一歩を踏み出した瞬間だった。`,
            summary: "魔法学園の新入生・山田太郎が実技試験を前に不安を抱えるが、天才少女・佐藤美咲の手助けで初めて火の魔法を成功させる物語。",
            title: "第1話"
          };
        
        case 'continue':
          return {
            success: true,
            novel_text: `　実技試験の日、太郎は緊張しながらも教室に向かった。廊下で美咲とすれ違うと、彼女は「がんばって！」と声をかけてくれた。その言葉を胸に、太郎は試験会場となる魔法実習室へと足を進めた。\n\n　「山田太郎君、次はあなたの番です」\n\n　鷹の目のように鋭い視線を持つグリフィス先生が太郎の名前を呼んだ。太郎は深呼吸をし、前日の練習を思い出しながら魔力を集中させた。\n\n　「集中...呼吸を整えて...」\n\n　太郎は美咲のアドバイスを心の中で繰り返した。手のひらに魔力が集まるのを感じる。しかし、その瞬間、隣の実習室から大きな爆発音がした。太郎は驚いて魔力のバランスを崩してしまった。\n\n　「危ない！」\n\n　太郎の手から飛び出したのは小さな火の玉ではなく、不安定な炎の渦だった。制御を失った炎は勢いよく天井へと向かい、火災報知器を作動させた。たちまち実習室には水が降り注ぎ、生徒たちは悲鳴を上げた。\n\n　「山田君！魔力の制御ができていません！」\n\n　グリフィス先生は厳しい表情で言ったが、素早く魔法で炎を消し、水も止めた。\n\n　「す、すみません...」\n\n　ずぶ濡れになった太郎は、恥ずかしさと申し訳なさで頭を下げた。クラスメイトたちからはくすくすと笑い声が聞こえてくる。この日を境に「暴走の太郎」というあだ名がつくだろうと思うと、胸が痛かった。\n\n　放課後、落ち込んだ太郎が校庭のベンチに座っていると、美咲が近づいてきた。\n\n　「大変だったね。でも、あれはすごいパワーだったよ」\n\n　「すごいって...ただの失敗だよ。みんなの前で恥をかいて」\n\n　太郎が沈んだ声で言うと、美咲は首を横に振った。\n\n　「違うよ。普通の一年生があんな強力な炎を出せるはずないんだ。君には特別な才能があるんだと思う」\n\n　「特別...？」\n\n　「実は校長先生も興味を持ったみたいだよ。明日、校長室に来るように言われたって」\n\n　美咲の言葉に太郎は驚いた。校長のブレイズ博士は伝説の魔法使いで、滅多に学生と会うことはないと聞いていた。\n\n　「これは君のチャンスかもしれないね！」\n\n　美咲の目は輝いていた。太郎の心に小さな希望の灯がともった。失敗だと思っていたことが、新たな道を開くことになるとは思ってもみなかった。`,
            summary: "実技試験で魔力を暴走させてしまった太郎だが、その強力な力に校長が興味を示し、特別な才能の可能性が示唆される。",
            title: "第2話"
          };
        
        default:
          return {
            success: false,
            error: '不明なモックタイプです'
          };
      }
    }
  }
  
  // グローバルAPIクライアントの初期化
  const apiClient = new AINovelAPI();