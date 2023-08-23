import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import os

class CustomRow:
    def __init__(self, parent, row_num, row_data, headers=False):
        self.parent = parent
        self.widgets = []
        self.row_data = row_data

        checkbtn = tk.Checkbutton(self.parent)
        checkbtn.grid(row=row_num, column=0, sticky="nsew")
        self.widgets.append(checkbtn)

        for col_idx, item in enumerate(row_data):
            if headers:
                label = tk.Label(self.parent, text=item, borderwidth=1, relief="solid", width=75)  # Set width to 75 to roughly equal 600px
                label.grid(row=row_num, column=col_idx+1, sticky="nsew")
                label.bind("<Button-1>", lambda event, idx=col_idx: parent.sort_by_column(idx))
                self.widgets.append(label)
            elif col_idx == 0:
                canvas = tk.Canvas(self.parent, width=600, height=300, bg='gray')
                canvas.grid(row=row_num, column=col_idx+1, sticky="nsew")
                canvas.bind("<Button-1>", self.open_image)
                self.load_image(item, canvas)
                self.widgets.append(canvas)
            else:
                label = tk.Label(self.parent, text=item, borderwidth=1, relief="solid", width=25)
                label.grid(row=row_num, column=col_idx+1, sticky="nsew")
                self.widgets.append(label)

    def load_image(self, image_path, canvas):
        if not image_path.strip() or not os.path.exists(image_path):
            return

        try:
            image = Image.open(image_path)
            width, height = image.size
            new_height = 300
            new_width = int((new_height/height) * width)
            image = image.resize((new_width, new_height), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")

    def open_image(self, event):
        col_idx = self.widgets.index(event.widget)
        image_path = self.row_data[col_idx]
        if image_path.strip():
            image = Image.open(image_path)
            image.show()

class CustomTable:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(self.parent)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.vscrollbar = tk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscrollbar.set)
        self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.grid_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind("<Configure>", self.on_frame_configure)

        self.row = 0  # Keep track of the current row number
        # Add table headers
        headers = ["Image", "Hash1", "Hash2", "Hash3", "Hash4", "Hash5"]  # Modify this list as per your CSV columns
        self.header_row = CustomRow(self.grid_frame, 0, headers)
        # Add placeholder rows
        for _ in range(5):  # Let's add 5 placeholder rows for now
            self.add_row([''] * 6)  # Assuming 6 columns
            
    def sort_by_column(self, col_idx):
        # Sort data based on the column index and re-populate the table
        self.data.sort(key=lambda x: x[col_idx])
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.header_row = CustomRow(self.grid_frame, 0, headers, headers=True)
        self.row = 1
        for row_data in self.data:
            self.add_row(row_data)
            
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta//120), "units")
        
    def add_row(self, row_data):
        CustomRow(self.grid_frame, self.row, row_data)
        self.row += 1

    def load_csv(self, file_path):
        # Clear all rows before adding new ones
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Add table headers again after clearing
        headers = ["Image", "Hash1", "Hash2", "Hash3", "Hash4", "Hash5"]
        self.header_row = CustomRow(self.grid_frame, 0, headers)
        self.row = 1  # Reset row counter after clearing rows
        
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row_data in reader:
                self.add_row(row_data)
class App:
    def __init__(self, root):
        self.table = CustomTable(root)
        self.load_button = tk.Button(root, text="Load CSV", command=self.load_csv)
        self.load_button.pack()

    def load_csv(self):
        file_path = filedialog.askopenfilename(title="Open CSV", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.table.load_csv(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x600")
    app = App(root)
    root.mainloop()