import cv2
import os
import time
import cupy as cp
import math

# 讀取txt檔
def read_txt(file_path):
    f = open(file_path, 'r')
    line = f.readline().split(' ')
    a = int(line[0])
    b = int(line[1])
    c = int(line[2])
    d = int(line[3])
    M = int(line[4])
    N = int(line[5])
    P = int(line[6])
    G = int(line[7])
    f.close()
    return a, b, c, d, M, N, P, G
# 找S
def find_S(t, p):
    S = 1
    while (S * t - 1) % p != 0:
        S = S + 1
    return S

# RT逆轉換g1
def inverse_rectangular_transform_g1(original_coords, a, b, c, d, M, N):
    t = a*d - b*c
    p = math.gcd(M, N)
    S = find_S(t, p)
    x_and_y_p= cp.mod(cp.dot((S * cp.array([[d, (p - 1) * b], [(p - 1) * c, a]])), original_coords), p)
    return x_and_y_p

# RT逆轉換g2
def inverse_rectangular_transform_g2(original_coords, x_and_y_p, a, b, c, d, M, N):
    p = math.gcd(M, N)
    h = M / p
    v = N / p
    H = ((original_coords[0] - (a * x_and_y_p[0]) - (b * x_and_y_p[1])) / p) + (math.ceil((a * p) / h) * h) + (math.ceil((b * p) / h) * h)
    V = ((original_coords[1] - (c * x_and_y_p[0]) - (d * x_and_y_p[1])) / p) + (math.ceil((c * p) / v) * v) + (math.ceil((d * p) / v) * v)
    return H, V

# RT逆轉換g3
def inverse_rectangular_transform_g3(H, V, a, b, c, d, M, N):
    p = math.gcd(M, N)
    h = M / p
    v = N / p
    if b % h == 0:
        x_h = (find_S(a, h) * H) %  h
        y_v = find_S(d, v) * (V + (math.ceil((c * h) / v) * v) - (c * x_h)) % v
    elif c % v == 0:
        y_v = (find_S(d, v) * V) % v
        x_h = find_S(a, h) * (H + (math.ceil((b * v) / h) * h) - (b * y_v)) % h
    return x_h, y_v

# RT逆轉換g4
def inverse_rectangular_transform_g4(x_and_y_p, x_h, y_v, M, N):
    p = math.gcd(M, N)
    x = x_and_y_p[0] + p * x_h
    y = x_and_y_p[1] + p * y_v
    return x.astype(int), y.astype(int)

# RT逆轉換
def inverse_rectangular_transform(image, a, b, c, d, M, N):
    image_gpu = cp.asarray(image)

    # 建立輸出圖像陣列
    image_change_gpu = cp.zeros_like(image_gpu)

    x_coords, y_coords = cp.meshgrid(cp.arange(M), cp.arange(N))
    original_coords = cp.stack([x_coords.flatten(), y_coords.flatten()], axis=0)

    x_and_y_p = inverse_rectangular_transform_g1(original_coords, a, b, c, d, M, N)
    H, V = inverse_rectangular_transform_g2(original_coords, x_and_y_p, a, b, c, d, M, N)
    x_h, y_v = inverse_rectangular_transform_g3(H, V, a, b, c, d, M, N)
    change_x, change_y = inverse_rectangular_transform_g4(x_and_y_p, x_h, y_v, M, N)

    # 更新像素值
    transformed_x = change_x.reshape(N, M).astype(cp.int32)
    transformed_y = change_y.reshape(N, M).astype(cp.int32)
    image_change_gpu[transformed_y, transformed_x] = image_gpu

    return cp.asnumpy(image_change_gpu)

#  輸出轉換時間txt
def write_txt(a, b, c, d, M, N, P, G, time, file_path):
    f = open(file_path, 'w')
    f.write(str(a) + " " + str(b) + " " + str(c) + " " + str(d) + " " + str(M) + " " + str(N) + " " + str(P) + " " + str(G) + " " + str(time) + '\n')
    f.close()

# 已加密圖片資料夾的路徑
folder_path = "encryp"

# 資料夾中所有圖片的名字
image_files = os.listdir(folder_path)


for image_file in image_files:

    # 開始逆轉換時間
    start_time = time.perf_counter()

    # 構建完整的文件路徑
    image_path = os.path.join(folder_path, image_file) 

    # 使用OpenCV讀取圖像
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # 讀取Secret-Key.txt
    a, b, c, d, M, N, P, G = read_txt('param/%s-EncKey.txt'%image_file[:-8])

    # 進行RT逆轉換
    for i in range(G):
        image = inverse_rectangular_transform(image, a, b, c, d, M, N)

    # 結束轉換時間
    end_time = time.perf_counter()

    #  輸出轉換時間txt
    write_txt(a, b, c, d, M, N, P, G, round((end_time - start_time), 2), 'results/%s_invdec_time.txt'%image_file[:-8])

    # 轉換後圖片檔名
    image_new_name = f'{image_file[:-8]}_invdec{image_file[-4:]}'

    # 保存圖像
    cv2.imwrite(f'invdec/{image_new_name}', image)