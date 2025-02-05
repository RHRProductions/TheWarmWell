import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import csv

def create_high_priority_module(parent_frame):
    """Initialize the High-Priority Follow-Ups module within the parent frame."""
    # Frame for the module
    frame = ttk.Frame(parent_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create the table
    tree = ttk.Treeview(frame, columns=("Name", "Phone", "City", "Notes", "Status", "Priority"), show="headings")
    tree.pack(fill="both", expand=True)

    # Define headings
    tree.heading("Name", text="Name")
    tree.heading("Phone", text="Phone")
    tree.heading("City", text="City")
    tree.heading("Notes", text="Notes")
    tree.heading("Status", text="Status")
    tree.heading("Priority", text="Priority")

    # Define column widths
    tree.column("Name", width=100)
    tree.column("Phone", width=100)
    tree.column("City", width=100)
    tree.column("Notes", width=200, stretch=True)
    tree.column("Status", width=150)
    tree.column("Priority", width=100)

    # Add scrollbars
    scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Load data from file or mock data
    def load_data():
        if os.path.exists("high_priority_followups.csv"):
            with open("high_priority_followups.csv", "r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header
                for row in reader:
                    tree.insert("", "end", values=row)
        else:
            mock_data = [
                ("Jane Doe", "555-123-4567", "Denver", "Follow-up within 24 hours.", "Immediate Follow-Up", "High"),
                ("John Smith", "555-987-6543", "Austin", "Needs to confirm appointment.", "Pending", "Medium"),
            ]
            for record in mock_data:
                tree.insert("", "end", values=record)

    def save_table():
        with open("high_priority_followups.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Phone", "City", "Notes", "Status", "Priority"])
            for row in tree.get_children():
                values = tree.item(row, "values")
                writer.writerow(values)

    def remove_entry():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No entry selected for removal!")
            return

        confirm = messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this entry?")
        if confirm:
            item_id = selected_item[0]
            tree.delete(item_id)
            save_table()
            messagebox.showinfo("Success", "Entry removed.")

    def add_entry():
        popup = tk.Toplevel(parent_frame)
        popup.title("Add Entry")
        popup.geometry("400x300")

        labels = ["Name", "Phone", "City", "Notes", "Status", "Priority"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label in ["Status", "Priority"]:
                options = ["Immediate Follow-Up", "Pending", "Closed"] if label == "Status" else ["High", "Medium", "Low"]
                var = tk.StringVar()
                dropdown = ttk.Combobox(popup, textvariable=var, values=options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries.append(var)
            else:
                entry = tk.Entry(popup, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries.append(entry)

        def save_new_entry():
            new_values = [entry.get() if isinstance(entry, tk.Entry) else entry.get() for entry in entries]
            if any(not value.strip() for value in new_values):
                messagebox.showerror("Error", "All fields must be filled!")
                return
            tree.insert("", "end", values=new_values)
            save_table()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_new_entry).grid(row=len(labels), column=0, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, pady=10)

    # Button Frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill="x", pady=5)

    ttk.Button(button_frame, text="Add Entry", command=add_entry).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Remove Entry", command=remove_entry).pack(side="left", padx=5)

    # Load initial data
    load_data()

    return frame
