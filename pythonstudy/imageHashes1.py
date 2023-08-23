import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
import imagehash
from PIL import Image
import csv
import os
from concurrent.futures import ThreadPoolExecutor

def select_images_or_folder():
    if folder_var.get():
        folder_path = filedialog.askdirectory()
        if folder_path:
            file_paths = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        file_paths.append(os.path.join(root, file))
    else:
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    
    if file_paths:
        total_images.set(len(file_paths))
        processed_images.set(0)
        with ThreadPoolExecutor(max_workers=int(thread_entry.get())) as executor:
            list(executor.map(process_image, file_paths))

def process_image(file_path):
    hash_values = generate_hashes(file_path)
    save_to_csv(hash_values)
    processed_images.set(processed_images.get() + 1)

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

def save_to_csv(hash_values):
    with open('hashes.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Image', 'Average Hash', 'Perceptual Hash', 'Difference Hash', 'Wavelet Hash', 'Color Hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat("hashes.csv").st_size == 0:
            writer.writeheader()
        writer.writerow(hash_values)

app = tk.Tk()
app.title("ImageHash GUI")

select_button = tk.Button(app, text="选择图片/文件夹", command=select_images_or_folder)
select_button.pack(pady=20)

folder_var = tk.BooleanVar(value=False)
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

thread_label = tk.Label(app, text="线程数:")
thread_label.pack(pady=5, anchor=tk.W)
thread_entry = tk.Entry(app)
thread_entry.pack(pady=5, anchor=tk.W, padx=20)
thread_entry.insert(0, "4")

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

app.mainloop()