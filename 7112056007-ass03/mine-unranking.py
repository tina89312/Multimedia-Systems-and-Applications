import math
import re

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
    input_str = input("(n, k, s10) = ")

    # 使用正則表達式拆解 n, k, s10
    match = re.match(r'\((\d+),\s*(\d+),\s*(\d+)\)', input_str)
    if match:
        n = int(match.group(1))
        k = int(match.group(2))
        s10 = int(match.group(3))

        # 計算組合表示法
        coefficients = unrank(n, k, s10)

        # 根據 n 和 k 決定 Board Size 和檔案名稱中的編號
        board_size, file_number = determine_board_size_and_file_number(n, k)
        output_file = f"Mine{file_number}.txt"
        with open(output_file, 'w') as f:
            # 輸出 Board Size, k，接著輸出拆解後的 coefficients
            f.write(f"{board_size} {k}\n")
            f.write(' '.join(map(str, coefficients)) + "\n")

if __name__ == "__main__":
    main()
