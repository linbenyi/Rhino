import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import csv
import os
import threading
from datetime import datetime
import imagehash
from PIL import Image

# 选择文件或文件夹
def select_file_or_directory():
    # 根据复选框的值来确定是选择文件还是文件夹
    if var.get() == "File":
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp;*.tiff")])
        if file_path:
            files.append(file_path)
    else:
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 选择文件夹下的所有图片文件
            import os
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        files.append(os.path.join(root, filename))
    
    # 保存文件名到CSV
    save_to_csv(files)

# 将文件名保存到CSV
def save_to_csv(files):
    global csv_filename
    csv_filename = datetime.now().strftime('%Y%m%d%H%M%S') + ".csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for file_path in files:
            writer.writerow([file_path])

# 主窗口
root = tk.Tk()
root.title("Image Hash GUI")

# 文件列表
files = []

# 创建复选框来选择是选择文件还是文件夹
var = tk.StringVar(value="File")
file_rb = tk.Radiobutton(root, text="选择文件", variable=var, value="File")
file_rb.pack(pady=10)
directory_rb = tk.Radiobutton(root, text="选择文件夹", variable=var, value="Directory")
directory_rb.pack(pady=10)

# 创建按钮来打开选择文件或文件夹的对话框
select_button = tk.Button(root, text="选择", command=select_file_or_directory)
select_button.pack(pady=20)

# 进度信息和进度条
processed_files = tk.IntVar(value=0)
total_files = tk.IntVar(value=0)

progress_label = tk.Label(root, text=f"Processed: {processed_files.get()}/{total_files.get()}")
progress_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=processed_files, maximum=100) # maximum will be updated later
progress_bar.pack(pady=20)

# 处理单个图片的哈希值
def process_image(file_path, results, hash_methods):
    try:
        image = Image.open(file_path)
        hash_values = []

        # 根据用户选择来计算哈希值
        if "dHash" in hash_methods:
            hash_values.append(str(imagehash.dhash(image)))
        if "pHash" in hash_methods:
            hash_values.append(str(imagehash.phash(image)))
        if "wHash" in hash_methods:
            hash_values.append(str(imagehash.whash(image)))
        if "ColorHash" in hash_methods:
            hash_values.append(str(imagehash.colorhash(image)))
        if "Average Hash" in hash_methods:
            hash_values.append(str(imagehash.average_hash(image)))

        results[file_path] = hash_values

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# 哈希方法的复选框
dhash_var = tk.BooleanVar()
dhash_cb = tk.Checkbutton(root, text="dHash", variable=dhash_var)
dhash_cb.pack(pady=5)

phash_var = tk.BooleanVar()
phash_cb = tk.Checkbutton(root, text="pHash", variable=phash_var)
phash_cb.pack(pady=5)

whash_var = tk.BooleanVar()
whash_cb = tk.Checkbutton(root, text="wHash", variable=whash_var)
whash_cb.pack(pady=5)

colorhash_var = tk.BooleanVar()
colorhash_cb = tk.Checkbutton(root, text="ColorHash", variable=colorhash_var)
colorhash_cb.pack(pady=5)

average_hash_var = tk.BooleanVar()
average_hash_cb = tk.Checkbutton(root, text="Average Hash", variable=average_hash_var)
average_hash_cb.pack(pady=5)


# 计算图片的哈希值（多线程版本）
def compute_hash_multithreaded():
    num_threads = int(threads_var.get())
    hash_methods = []

    # 收集用户选择的哈希方法
    if dhash_var.get():
        hash_methods.append("dHash")
    if phash_var.get():
        hash_methods.append("pHash")
    if whash_var.get():
        hash_methods.append("wHash")
    if colorhash_var.get():
        hash_methods.append("ColorHash")
    if average_hash_var.get():
        hash_methods.append("Average Hash")

    # 读取之前生成的CSV文件中的图片文件
    with open(csv_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        files_from_csv = [row[0] for row in reader]

    # 创建一个字典来保存结果
    results = {}

    # 创建并启动线程
    threads = []
    for file_path in files_from_csv:
        thread = threading.Thread(target=process_image, args=(file_path, results, hash_methods))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 更新CSV文件
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for file_path, hash_values in results.items():
            writer.writerow([file_path] + hash_values)

# 推荐的线程数（通常为CPU核心数）
recommended_threads = os.cpu_count()



# 输入框供用户选择线程数
threads_var = tk.StringVar(value=str(recommended_threads))
threads_label = tk.Label(root, text="选择线程数 (推荐值: {})".format(recommended_threads))
threads_label.pack(pady=10)
threads_entry = tk.Entry(root, textvariable=threads_var)
threads_entry.pack(pady=10)

# 创建一个按钮来开始计算哈希值
compute_button = tk.Button(root, text="Compute Hash", command=compute_hash_multithreaded)
compute_button.pack(pady=20)
root.mainloop()