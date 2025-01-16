祕密訊息產生地雷地位置程式(mine-unranking.py)：
	1.使用到套件math、re
	2.依據提示輸入n、k、測試次數、祕密訊息檔案位置後程式會將地雷位置檔案存放在2-Locat資料夾中

地雷程式(minesweeper-master/mine-entropy.py)：
	1.使用到套件os、glob、math、pygame、time、statistics
	2.依據提示選擇使用地雷位置檔案進行測試並選擇測試的遊戲等級，程式會自動進行遊戲並將結果圖存在3-Marke資料夾中，而count與entropy等資訊等檔案會存在7-Entro資料夾中

解密程式(auto-extract.py)：
	1.使用到套件os、re、cv2、numpy、math、copy
	2.程式會自動將3-Marke資料夾中的圖片進行解密，解密訊息檔案存放在6-Extra資料夾中
