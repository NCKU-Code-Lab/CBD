## Workflow
1. 搜尋建築案例，一般而言建築案例會由文字敘述與圖片組成，而圖片又可以大致分為建築圖面、照片或渲染圖、diagrams。
2. 對圖片進行預處理。

   創建一個專門進行預處理的「我的 GPT / MyGPT」 ，指令欄輸入 03_preprocess prompt.md 的內容。餵 LLMs 時再註明分類屬於 P1/P2/P3。

   *在每一次預處理開始前，先請 LLMs 建立 canvas 檔案，並依案例命名方便後續叫出檔案使用，預處理完成後請 LLMs 把結果紀錄至 canvas 檔案內*
3. 使用 AI (ChatGPT) 進行案例分析：
   
   輸入 04_precedent DNA analysis prompt.md。
   
   餵給 GPT 的資料有：圖片預處理後產生的文字＋原本案例敘述的文字
5. 確認內容正確後，以 05_package example.json 作為範例 (input)，將分析內容統一打包成 JSON 格式 (output)。
