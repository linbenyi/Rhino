import tkinter as tk
from tkinter import ttk, filedialog
import csv
import threading

class CSVLoader(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("CSV Loader")
        self.geometry("400x150")
        
        # Button to open CSV
        self.open_button = tk.Button(self, text="Open CSV", command=self.open_csv_file)
        self.open_button.pack(pady=10)
        
        # Label to show the state
        self.state_label = tk.Label(self, text="Please open a CSV file...")
        self.state_label.pack(pady=10)
        
        # Progressbar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)
        
    def open_csv_file(self):
        file_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if file_path:
            self.csv_file = file_path
            self.total_lines = sum(1 for line in open(file_path))
            # Start the loading thread
            self.thread = threading.Thread(target=self.load_csv)
            self.thread.start()
        
    def load_csv(self):
        with open(self.csv_file, "r") as file:
            csv_reader = csv.reader(file)
            for index, row in enumerate(csv_reader):
                # Update the GUI
                self.update_progress(index + 1)
                
    def update_progress(self, current_line):
        self.state_label.config(text=f"Loaded {current_line}/{self.total_lines} lines")
        self.progress['value'] = (current_line / self.total_lines) * 100
        self.update_idletasks()

# Test
app = CSVLoader()
app.mainloop()