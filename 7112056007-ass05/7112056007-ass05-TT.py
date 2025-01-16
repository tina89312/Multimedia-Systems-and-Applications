import cv2
import os
import time
import cupy as cp

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

# RT轉換 (GPU版本)
def rectangular_transform_gpu(image, a, b, c, d, M, N):
    # 將圖像和參數轉為 GPU 上的陣列
    image_gpu = cp.asarray(image)
    A_gpu = cp.array([[a, b], [c, d]])

    # 建立輸出圖像陣列
    image_change_gpu = cp.zeros_like(image_gpu)

    # 計算新座標
    x_coords, y_coords = cp.meshgrid(cp.arange(M), cp.arange(N))
    original_coords = cp.stack([x_coords.flatten(), y_coords.flatten()], axis=0)
    transformed_coords = cp.mod(cp.dot(A_gpu, original_coords), cp.array([[M], [N]]))

    # 更新像素值
    transformed_x = transformed_coords[0].reshape(N, M).astype(cp.int32)
    transformed_y = transformed_coords[1].reshape(N, M).astype(cp.int32)
    image_change_gpu[transformed_y, transformed_x] = image_gpu

    # 將結果從 GPU 返回至 CPU
    return cp.asnumpy(image_change_gpu)

#  輸出轉換時間txt
def write_txt(a, b, c, d, M, N, P, G, time, file_path):
    f = open(file_path, 'w')
    f.write(str(a) + " " + str(b) + " " + str(c) + " " + str(d) + " " + str(M) + " " + str(N) + " " + str(P) + " " + str(G) + " " + str(time) + '\n')
    f.close()

#加密

# 圖片資料夾的路徑
folder_path = "source"

# 資料夾中所有圖片的名字
image_files = os.listdir(folder_path)

for image_file in image_files:

    # 開始轉換時間
    start_time = time.perf_counter()

    # 構建完整的文件路徑
    image_path = os.path.join(folder_path, image_file) 

    # 使用OpenCV讀取圖像
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # 讀取Secret-Key.txt
    a, b, c, d, M, N, P, G= read_txt('param/%s-EncKey.txt'%image_file[:-4])

    # 進行RT轉換
    for i in range(G):
        image = rectangular_transform_gpu(image, a, b, c, d, M, N)

    # 結束轉換時間
    end_time = time.perf_counter()

    #  輸出轉換時間txt
    write_txt(a, b, c, d, M, N, P, G, round((end_time - start_time), 2), 'results/%s_enc_result.txt'%image_file[:-4])

    # 轉換後圖片檔名
    image_new_name = image_file[:-4] + '_enc' + image_file[-4:]

    # 保存圖像
    cv2.imwrite('encryp/%s'%image_new_name, image)


#解密

# 圖片資料夾的路徑
encryp_folder_path = "encryp"

# 資料夾中所有圖片的名字
encryp_image_files = os.listdir(encryp_folder_path)

for image_file in encryp_image_files:

    # 開始轉換時間
    start_time = time.perf_counter()

    # 構建完整的文件路徑
    encryp_image_path = os.path.join(encryp_folder_path, image_file) 

    # 使用OpenCV讀取圖像
    encryp_image = cv2.imread(encryp_image_path, cv2.IMREAD_UNCHANGED)

    # 讀取Secret-Key.txt
    a, b, c, d, M, N, P, G = read_txt('param/%s-EncKey.txt'%image_file[:-8])

    # 進行RT轉換
    for i in range(P - G):
        encryp_image = rectangular_transform_gpu(encryp_image, a, b, c, d, M, N)

    # 結束轉換時間
    end_time = time.perf_counter()

    #  輸出轉換時間txt
    write_txt(a, b, c, d, M, N, P, G, round((end_time - start_time), 2), 'results/%s_for_result.txt'%image_file[:-8])

    # 轉換後圖片檔名
    image_new_name = image_file[:-8] + '_fordec' + image_file[-4:]

    # 保存圖像
    cv2.imwrite('fordec/%s'%image_new_name, encryp_image)
