import math
import re

def read_secret_characters(file_path, start_char, r):
    # 讀取檔案內容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 確保檔案長度足夠
    if len(content) < r:
        raise ValueError(f"File has less than {r} characters.")
    
    # 取出前 r 個字元
    secret_chars = content[start_char : start_char + r]
    
    return secret_chars

def chars_to_binary_string(chars):
    # 將每個字元轉換成8-bit二進制
    binary_string = ''.join(format(ord(char), '08b') for char in chars)
    
    return binary_string

def binary_to_decimal(binary_string):
    # 將二進制字串轉換成十進制數值
    return int(binary_string, 2)

# 計算組合數 C(n, k)
def combination(n, k):
    if k > n:
        return 0
    return math.comb(n, k)

# Unranking：將 s10 轉換為組合係數表示法
def unrank(n, k, m):
    coefficients = []
    current_m = m
    for i in range(k, 0, -1):
        # 找到最大的 sk 使得 C(i, sk) <= m
        sk = n - 1
        while combination(sk, i) > current_m:
            sk -= 1
        coefficients.append(sk)
        current_m -= combination(sk, i)
        n = sk
    return coefficients

# 根據 n 和 k 決定 Board Size 和對應的檔案編號
def determine_board_size_and_file_number(n, k):
    if n == 81 and k == 10:
        return "9 9", 1
    elif n == 256 and k == 40:
        return "16 16", 2
    elif n == 480 and k == 99:
        return "30 16", 3
    elif n == 720 and k == 120:
        return "30 24", 4
    elif n == 720 and k == 360:
        return "30 24", 5

# 主程式：讓使用者輸入 (n, k, s10) 格式並計算組合係數
def main():
    # 使用者輸入格式
    input_str = input("(n, k, times) = ")

    secret_file = input("秘密訊息檔案位置:")

    # 使用正則表達式拆解 n, k, s10
    match = re.match(r'\((\d+),\s*(\d+),\s*(\d+)\)', input_str)

    if match:
        n = int(match.group(1))
        k = int(match.group(2))
        times = int(match.group(3))

        r = math.floor(math.floor(math.log2(combination(n, k))) / 8)  # 假設需要讀入的字元數
        L = r * 8  # 每個字元是8-bit，L表示所有字元的二進制總長度

        for i in range(times):

            # 讀取秘密字元
            secret_chars = read_secret_characters(secret_file, i * r, r)

            # 轉換成L-bit二進制字串
            secret_binary_string = chars_to_binary_string(secret_chars)

            # 轉換為十進制數值
            s10 = binary_to_decimal(secret_binary_string[:L])

            # 計算組合表示法
            coefficients = unrank(n, k, s10)

            # 根據 n 和 k 決定 Board Size 和檔案名稱中的編號
            board_size, file_number = determine_board_size_and_file_number(n, k)

            secret_chars_file = f"4-Embed/Mine{file_number}_Embed_Char_{i+1:03}.txt"
            with open(secret_chars_file, 'w') as f:
                # 輸出秘密訊息
                f.write(f'{secret_binary_string}\n')
                f.write(f'{s10}\n')
                f.write(f'{secret_chars}\n\n')

            output_file = f"2-Locat/Mine{file_number}_{i+1:03}.txt"
            with open(output_file, 'w') as f:
                # 輸出 Board Size, k，接著輸出拆解後的 coefficients
                f.write(f"{board_size} {k}\n")
                f.write(' '.join(map(str, coefficients)) + "\n")


if __name__ == "__main__":
    main()