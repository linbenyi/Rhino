import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import datetime

# Calculate Hamming distance between two hashes
def hamming_distance(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def load_csv():
    filepath = filedialog.askopenfilename(title="Select CSV File", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    if not filepath:
        return

    threading.Thread(target=populate_data, args=(filepath,)).start()




def populate_data(filepath):
    global data
    data = pd.read_csv(filepath)

    tree.delete(*tree.get_children())
    for index, row in data.iterrows():
        image_path = row[0]
        img = Image.open(image_path)
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(image_path)).strftime('%Y-%m-%d %H:%M:%S')
        modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(image_path)).strftime('%Y-%m-%d %H:%M:%S')
        tree.insert("", "end", values=(image_path, 
                                       img.format, 
                                       f"{img.width}x{img.height} {img.mode}", 
                                       f"{os.path.getsize(image_path)} bytes", 
                                       creation_time,
                                       modification_time,
                                       row[1], row[2], row[3], row[4], row[5]))

def on_item_selected(event):
    for treeview in [tree, detail_tree]:
        if treeview.selection():
            item = treeview.selection()[0]
            image_path = treeview.item(item, "values")[0]
            
            img = Image.open(image_path)
            max_size = 600
            scale = min(max_size/img.width, max_size/img.height)
            img = img.resize((int(img.width*scale), int(img.height*scale)))
            img = ImageTk.PhotoImage(img)
            
            if treeview == tree:
                preview_label1.config(image=img)
                preview_label1.image = img
            else:
                preview_label2.config(image=img)
                preview_label2.image = img

def on_hash_clicked(event):
    clicked_column = tree.identify_column(event.x)
    if not clicked_column.startswith("#"):
        return

    col_index = int(clicked_column.replace("#", ""))
    if col_index < 7:
        return

    hash_value = tree.item(tree.selection()[0], "values")[col_index-1]
    
    distances = []
    for child in tree.get_children():
        distance = hamming_distance(tree.item(child, "values")[col_index-1], hash_value)
        distances.append((distance, tree.item(child, "values")))

    distances.sort(key=lambda x: x[0])
    similar_items = distances[:20]

    detail_tree.delete(*detail_tree.get_children())
    for distance, values in similar_items:
        detail_tree.insert("", "end", values=values)

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
    
# Search Function
def search():
    search_term = search_var.get().lower()
    for item in tree.get_children():
        values = tree.item(item, "values")
        if any(search_term in str(val).lower() for val in values):
            tree.selection_set(item)
            tree.see(item)
            break
root = tk.Tk()
root.title("Find Similar Images")
root.geometry("1600x1000")

frame0 = ttk.Frame(root, padding="10")
frame1 = ttk.Frame(root, padding="10")
frame2 = ttk.Frame(root, padding="10")
frame3 = ttk.Frame(root, padding="10")

# Search Entry
search_var = tk.StringVar()
def on_search():
    search_term = search_var.get()
    # Highlight and select the matching item
    for child in tree.get_children():
        if search_term in tree.item(child, "values")[0] or search_term in tree.item(child, "values")[6:]:  # filename or hash value
            tree.selection_set(child)
            tree.focus(child)
            break
# Search Button
search_entry = ttk.Entry(frame0, textvariable=search_var)
search_entry.pack(side="left", padx=5)
search_btn = ttk.Button(frame0, text="Search", command=on_search)
search_btn.pack(side="left", padx=5)

# Instructions
instructions = ttk.Label(frame0, text="Load the CSV and then select a hash from the table above")
instructions.pack(side="left", padx=5)

# Load CSV Button
load_btn = ttk.Button(frame0, text="Load CSV", command=load_csv)
load_btn.pack(side="left", padx=5)

frame0.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame1.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame2.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame3.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# This ensures the frames take up equal vertical space

root.grid_rowconfigure(0, weight=2, minsize=30)
root.grid_rowconfigure(1, weight=1, minsize=300)
root.grid_rowconfigure(2, weight=1, minsize=300)
root.grid_rowconfigure(3, weight=1, minsize=300)

columns = ("Image Path", "Type", "Dimensions", "Size", "Creation Time", "Modification Time", "Hash1", "Hash2", "Hash3", "Hash4", "Hash5")
column_widths = [290, 40, 110, 100, 140, 140, 140, 140, 140, 140, 140]
tree = ttk.Treeview(frame1, columns=columns, show="headings")

for i, col in enumerate(columns):
    tree.column(col, width=column_widths[i])
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
tree.bind("<<TreeviewSelect>>", on_item_selected)
tree.bind("<Button-1>", on_hash_clicked)

# Adding scrollbar inside the treeview
#scrollbar1 = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
#scrollbar1.pack(side="right", fill="y")

# Vertical Scrollbar
scrollbar1_v = ttk.Scrollbar(frame1, orient="vertical", command=tree.yview)
scrollbar1_v.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar1_v.set)

# Horizontal Scrollbar
scrollbar1_h = ttk.Scrollbar(frame1, orient="horizontal", command=tree.xview)
scrollbar1_h.pack(side="bottom", fill="x")
tree.configure(xscrollcommand=scrollbar1_h.set)

# Pack the tree
tree.pack(pady=20, fill=tk.BOTH, expand=True, side="left")

preview_frame = ttk.Frame(frame2)
preview_frame.pack(pady=10, fill=tk.X)

preview_label1 = ttk.Label(preview_frame)
preview_label1.pack(side="left", padx=10)

preview_label2 = ttk.Label(preview_frame)
preview_label2.pack(side="left", padx=10)

detail_tree = ttk.Treeview(frame3, columns=columns, show="headings")
# Setting treeview width to match window width minus scrollbar width
# treeview_width = 1200 - 20  # 20 pixels for scrollbar width
# total_column_widths = sum(column_widths)
# scale_factor = treeview_width / total_column_widths

for i, col in enumerate(columns):
    detail_tree.column(col, width=column_widths[i])
    detail_tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(detail_tree, _col, False))
detail_tree.bind("<<TreeviewSelect>>", on_item_selected)

# Adding scrollbar inside the detail_treeview
#scrollbar2 = ttk.Scrollbar(detail_tree, orient="vertical", command=detail_tree.yview)
#scrollbar2.pack(side="right", fill="y")
#detail_tree.configure(yscrollcommand=scrollbar2.set)
#detail_tree.pack(pady=20, fill=tk.BOTH, expand=True)

# Vertical Scrollbar
scrollbar2_v = ttk.Scrollbar(frame3, orient="vertical", command=detail_tree.yview)
scrollbar2_v.pack(side="right", fill="y")
detail_tree.configure(yscrollcommand=scrollbar2_v.set)

# Horizontal Scrollbar
scrollbar2_h = ttk.Scrollbar(frame3, orient="horizontal", command=detail_tree.xview)
scrollbar2_h.pack(side="bottom", fill="x")
detail_tree.configure(xscrollcommand=scrollbar2_h.set)

# Pack the detail_tree
detail_tree.pack(pady=20, fill=tk.BOTH, expand=True, side="left")

# Move the instructions, load_btn, and tree to frame1
instructions.master = frame1
load_btn.master = frame1
tree.master = frame1

# Move the preview_frame to frame2
preview_frame.master = frame2

# Move the detail_tree to frame3
detail_tree.master = frame3

root.mainloop()