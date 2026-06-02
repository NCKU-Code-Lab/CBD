## Workflow
1. 搜尋建築案例，一般而言建築案例會由文字敘述與圖片組成，而圖片又可以大致分為建築圖面、照片或渲染圖、diagrams。
2. 對圖片進行預處理。

   創建一個專門進行預處理的「我的 GPT / MyGPT」 ，指令欄輸入 03_preprocess prompt.md 的內容。餵 LLMs 時再註明分類屬於 P1/P2/P3。

   *在每一次預處理開始前，先請 LLMs 建立 canvas 檔案，並依案例命名方便後續叫出檔案使用，預處理完成後請 LLMs 把結果紀錄至 canvas 檔案內*
3. 使用 AI (ChatGPT) 進行案例分析：
   
   輸入 04_precedent DNA analysis prompt.md。
   
   餵給 GPT 的資料有：圖片預處理後產生的文字＋原本案例敘述的文字
5. 確認內容正確後，以 05_package example.json 作為範例 (input)，將分析內容統一打包成 JSON 格式 (output)。

## 工具簡介
**(一) 名稱**：Precedent DNA

**(二) 用途/目的**：整理建築案例知識

**(三) 使用者**：AI 知識庫的建構者

**(四) 使用範例** : 如下圖所示，完整對話範例請見前面 workflow 說明。

## Precedent DNA 介紹
**(一) Precedent DNA** 是參考 Oxman & Oxman（1993；1994）提出的「設計故事模組（Design Story）」結構，以【issue－concept－form】的結構為思考起點而發展出的一套案例知識整理方法。

**(二) 概念**：為因應大型語言模型(LLMs)對 tokens 的處理方式，precedent DNA 以建築語意模組取代冗長的敘事語意(如 Design Story)。

**(三) 結構**：Gene_A～Gene_Ｄ
1. Gene_A：Context 條件與脈絡
   * 說明基地、功能、文化脈絡或設計限制
2. Gene_B：Design Intentions 意圖
   * Issue（空間面對的挑戰）＋Concept（抽象設計理念）＋Strategy（實作空間策略）
3. Gene_C：Form 空間構成
   * C1: Vocabulary（重要空間語彙）
   * C2: Semantic Relations（空間之間的語意連接關係）
   * 結構為語法節點 S+V+O
     
      其中，Relation 的種類分為以下七種：
       - Spatial Relation（空間位置）
       - Circulation Relation（動線與流動）
       - Perceptual Relation（視覺感知、空間經驗）
       - Functional Relation（機能支援／隔離／整合）
       - Conceptual Relation（抽象設計理念間關聯）
       - Material Relation（材質構成／包覆／接合）
       - **Other（LLMs 可請行新增）
4. Gene_D：Feedback 結果與回饋
   * 包含使用者感受、設計者反思，或者 AI 自行推測可能的設計回饋與檢討

**(四) 形式**：最後會以 JSON 封裝，範例請見 05_precedent_10cases.json
