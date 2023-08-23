import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib

def get_md5(filename):
    """计算文件的MD5值"""
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def rename_files(directory, progress_var):
    """重命名文件"""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    counter = 1
    renamed_files = 0

    for file in files:
        filepath = os.path.join(directory, file)
        base, ext = os.path.splitext(file)
        if base.count('(') == 1 and base.count(')') == 1 and base.index('(') < base.index(')'):
            prefix, rest = base.split('(', 1)
            suffix, _ = rest.split(')', 1)
            new_name = f"{suffix}_{'{:05}'.format(counter)}{ext}"
            counter += 1
            new_path = os.path.join(directory, new_name)
            os.rename(filepath, new_path)
            renamed_files += 1
        progress_var.set(renamed_files / len(files) * 100)

def remove_duplicates(directory, skip_confirmation, progress_var):
    """删除重复文件"""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    seen_hashes = set()
    duplicates_removed = 0

    for file in files:
        filepath = os.path.join(directory, file)
        file_hash = get_md5(filepath)

        if file_hash in seen_hashes:
            if not skip_confirmation:
                if not messagebox.askyesno("确认", f"是否删除重复文件 {file}?"):
                    continue
            os.remove(filepath)
            duplicates_removed += 1
        else:
            seen_hashes.add(file_hash)
        progress_var.set(duplicates_removed / len(files) * 100)

def browse_directory(skip_confirmation_var, rename_progress_var, duplicate_progress_var):
    """选择目录并执行重命名和删除操作"""
    directory = filedialog.askdirectory()
    if not directory:
        return
    rename_files(directory, rename_progress_var)
    remove_duplicates(directory, skip_confirmation_var.get(), duplicate_progress_var)

# 创建GUI界面
root = tk.Tk()
root.title("文件处理工具")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="选择一个目录来重命名文件和删除重复项")
label.pack(pady=20)

skip_confirmation_var = tk.BooleanVar()
skip_confirmation_check = tk.Checkbutton(frame, text="删除重复文件时跳过确认", variable=skip_confirmation_var)
skip_confirmation_check.pack(pady=10)

browse_btn = tk.Button(frame, text="选择目录", command=lambda: browse_directory(skip_confirmation_var, rename_progress_var, duplicate_progress_var))
browse_btn.pack(pady=10)

rename_progress_var = tk.DoubleVar()
rename_progress = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate", variable=rename_progress_var)
rename_progress.pack(pady=10)
rename_label = tk.Label(frame, text="重命名进度")
rename_label.pack(pady=5)

duplicate_progress_var = tk.DoubleVar()
duplicate_progress = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate", variable=duplicate_progress_var)
duplicate_progress.pack(pady=10)
duplicate_label = tk.Label(frame, text="删除重复文件进度")
duplicate_label.pack(pady=5)

root.mainloop()