import csv
import tkinter as tk
from tkinter import filedialog, ttk

def view_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Clear the Treeview
            for row in tree.get_children():
                tree.delete(row)

            # Add the CSV content to the Treeview
            for row_number, row in enumerate(reader):
                if row_number == 0:
                    tree['columns'] = row
                    for col in row:
                        tree.heading(col, text=col)
                        tree.column(col, width=100)
                else:
                    tree.insert('', 'end', values=row)
    except FileNotFoundError:
        print("Error: File not found. Please check the file path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        view_csv(file_path)

# Create the main application window
root = tk.Tk()
root.title("CSV Viewer")
root.geometry("800x600")

# Create a frame for the Treeview
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Create a Treeview widget
columns = ()
tree = ttk.Treeview(frame, columns=columns, show='headings')
tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

# Add a scrollbar
scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scrollbar.set)

# Add a button to open CSV files
button = tk.Button(root, text="Open CSV File", command=open_file)
button.pack(pady=10)

# Run the application
root.mainloop()
