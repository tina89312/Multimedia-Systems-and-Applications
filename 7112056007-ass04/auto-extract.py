import os
import re
import cv2
import numpy as np
import math
import copy

# 讀取影像並轉換為灰階
def read_and_convert_to_gray(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray

# 地雷辨識與匹配
def detect_mines(gray_image, mine_template, threshold=0.95):
    result = cv2.matchTemplate(gray_image, mine_template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    return locations

# 在影像上框選地雷位置
def draw_mines(img, locations, mine_template):
    h, w = mine_template.shape[:2]
    for pt in zip(*locations[::-1]):
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 165, 255), 2)
    return img

# 計算組合數 C(n, k)
def combination(n, k):
    if k > n:
        return 0
    return math.comb(n, k)

# ranking：將組合係數表示法轉換為s10
def rank(k, m):
    m_ascending_order = copy.deepcopy(m)
    m_ascending_order.sort()  # 將地雷位置排序
    s10 = 0
    
    # 依據地雷的位置計算s10
    for i in range(k):
        s10 += combination(m_ascending_order[i], i + 1)
    return s10

# 二進制轉字串
def binary_to_string(binary_str):
    # 將二進制字符串補零，確保長度能被8整除
    binary_str = binary_str.zfill((len(binary_str) + 7) // 8 * 8)
    
    # 將二進制字符串按每 8 位分組
    chars = []
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i + 8]  # 取得每個字節（8 位）
        n = int(byte, 2)  # 將二進制轉換為十進制
        chars.append(chr(n))  # 將十進制轉換為字符並添加到列表中
    return ''.join(chars)  # 返回最終的字串

# 儲存地雷位置與提取秘密訊息
def save_mine_positions_and_message(locations, width, height, mine_count, cell_size, output_txt, mode):
    positions = sorted([round((x - 23) / cell_size) * width + round((y - 23) / cell_size) for x, y in zip(locations[0], locations[1])], reverse=True)
    secret_message_decimal = rank(mine_count, positions)
    secret_message_binary = bin(secret_message_decimal)[2:]
    secret_char = binary_to_string(secret_message_binary)
    
    # 儲存位置
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(f'{width} {height} {mine_count}\n')
        f.write(' '.join(map(str, positions)) + '\n')
    # 儲存秘密訊息
    if mode == 0:
        with open('Secret_Char_Extract.txt', 'w', encoding='utf-8') as f:
            f.write(f'{secret_message_binary}\n')
            f.write(f'{secret_message_decimal}\n')
            f.write(f'{secret_char}\n\n')
    else:
        with open('Secret_Char_Extract.txt', 'a', encoding='utf-8') as f:
            f.write(f'{secret_message_binary}\n')
            f.write(f'{secret_message_decimal}\n')
            f.write(f'{secret_char}\n\n')

# 尋找符合特定名稱格式的檔案
def find_images_with_pattern(pattern):
    files = os.listdir('.')
    image_files = [f for f in files if re.match(pattern, f)]
    return image_files

# 主程式
def auto_extract(image_path, mine_template_path, width, height, mine_count, cell_size, mode):
    img, gray = read_and_convert_to_gray(image_path)
    mine_template = cv2.imread(mine_template_path, 0)
    
    # 偵測地雷位置
    locations = detect_mines(gray, mine_template)
    
    # 繪製辨識影像
    img_with_mines = draw_mines(img, locations, mine_template)
    cv2.imwrite(image_path.replace('.png', '_Rec.png'), img_with_mines)
    
    # 儲存地雷位置與秘密訊息
    save_mine_positions_and_message(locations, width, height, mine_count, cell_size, image_path.replace('.png', '.txt'), mode)

# 執行範例
if __name__ == "__main__":
    # 定義圖片名稱格式的正則表達式
    pattern = r'Mine_\d+_\d+_\d+_Mark\.png'
    
    # 找尋符合格式的圖片檔案
    image_files = find_images_with_pattern(pattern)

    # 用於判定Secret_Char_Extract.txt是要用寫入並覆蓋還是續寫的模式
    mode = 0
    
    for image_file in image_files:
        # 遊戲板的寬、高與地雷數量
        match = re.match(r'Mine_(\d+)_(\d+)_(\d+)_Mark\.png', image_file)
        width = int(match.group(1))
        height = int(match.group(2))
        mine_count = int(match.group(3))
        
        # 根據圖片名稱選擇適當的地雷模板
        mine_template_path = 'Mine image/Mine_Beg.png' if width == 9 else 'Mine image/Mine_Inter.png' if width == 16 else 'Mine image/Mine_Expert.png'
        
        # 根據圖片名稱選擇適當的地雷尺寸
        cell_size = 84 if width == 9 else 47 if width == 16 else 25

        # 自動提取地雷位置和秘密訊息
        auto_extract(image_file, mine_template_path, width, height, mine_count, cell_size, mode)

        mode = 1


