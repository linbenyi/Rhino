import tkinter as tk
from tkinter import filedialog, ttk
import imagehash
from PIL import Image
import csv
import os
import threading
from queue import Queue

def select_files_or_folder():
    if folder_var.get():
        folder_path = filedialog.askdirectory()
        if folder_path:
            file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        else:
            return
    else:
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    
    if file_paths:
        total_images.set(len(file_paths))
        processed_images.set(0)
        app.update_idletasks()
        start_hashing(file_paths)

def worker():
    while True:
        file_path = file_queue.get()
        if file_path is None:
            break
        hash_values = generate_hashes(file_path)
        with lock:
            hashes.append(hash_values)
            processed_images.set(processed_images.get() + 1)
        file_queue.task_done()

def start_hashing(file_paths):
    for file_path in file_paths:
        file_queue.put(file_path)
    
    for _ in range(10):  # 10 threads
        threading.Thread(target=worker).start()

    app.after(100, check_hashing_complete)

def check_hashing_complete():
    if file_queue.empty():
        save_to_csv(hashes)
    else:
        app.after(100, check_hashing_complete)

def generate_hashes(file_path):
    with Image.open(file_path) as img:
        hash_values = {'Image': os.path.basename(file_path)}
        if ahash_var.get():
            hash_values['Average Hash'] = str(imagehash.average_hash(img))
        if phash_var.get():
            hash_values['Perceptual Hash'] = str(imagehash.phash(img))
        if dhash_var.get():
            hash_values['Difference Hash'] = str(imagehash.dhash(img))
        if whash_var.get():
            hash_values['Wavelet Hash'] = str(imagehash.whash(img))
        if colorhash_var.get():
            hash_values['Color Hash'] = str(imagehash.colorhash(img))
    return hash_values

def save_to_csv(hashes):
    with open('hashes.csv', 'w', newline='') as csvfile:
        fieldnames = ['Image', 'Average Hash', 'Perceptual Hash', 'Difference Hash', 'Wavelet Hash', 'Color Hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for hash_values in hashes:
            writer.writerow(hash_values)
    result_label.config(text="哈希值已保存到hashes.csv")

app = tk.Tk()
app.title("ImageHash GUI")

select_button = tk.Button(app, text="选择文件/文件夹", command=select_files_or_folder)
select_button.pack(pady=20)

folder_var = tk.BooleanVar()
tk.Checkbutton(app, text="选择文件夹", variable=folder_var).pack(anchor=tk.W)

ahash_var = tk.BooleanVar(value=True)
phash_var = tk.BooleanVar(value=True)
dhash_var = tk.BooleanVar(value=True)
whash_var = tk.BooleanVar(value=True)
colorhash_var = tk.BooleanVar(value=True)

tk.Checkbutton(app, text="Average Hash", variable=ahash_var).pack(anchor=tk.W)
tk.Checkbutton(app, text="Perceptual Hash", variable=phash_var).pack(anchor=tk.W)
tk.Checkbutton(app, text="Difference Hash", variable=dhash_var).pack(anchor=tk.W)
tk.Checkbutton(app, text="Wavelet Hash", variable=whash_var).pack(anchor=tk.W)
tk.Checkbutton(app, text="Color Hash", variable=colorhash_var).pack(anchor=tk.W)

progress = ttk.Progressbar(app, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress.pack(pady=20)

total_images = tk.IntVar()
processed_images = tk.IntVar()
progress_label = tk.Label(app, textvariable=tk.StringVar(value="Processed: 0 / 0"), font=("Arial", 12))
progress_label.pack(pady=10)

def update_progress_label(*args):
    progress_label['text'] = f"Processed: {processed_images.get()} / {total_images.get()}"
    progress['maximum'] = total_images.get()
    progress['value'] = processed_images.get()

total_images.trace_add("write", update_progress_label)
processed_images.trace_add("write", update_progress_label)

result_label = tk.Label(app, text="")
result_label.pack(pady=20)

file_queue = Queue()
hashes = []
lock = threading.Lock()

app.mainloop()