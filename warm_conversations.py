import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import csv
from datetime import datetime

def create_warm_conversations_module(parent_frame):
    """Creates the Warm Conversations module within the provided parent frame."""
    # Columns for warm leads
    columns = [
        "Name",
        "Phone",
        "City",
        "Notes",
        "Status",
        "Priority",
        "Last Conversation",
        "Next Follow-Up"
    ]

    # Frame for the table
    frame = ttk.Frame(parent_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview widget for displaying data
    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )
    tree.pack(fill="both", expand=True)

    # Define headings/column widths
    for col in columns:
        if col == "Last Conversation":
            tree.heading(col, text="Last Conversation (MM.DD.YYYY)")
            tree.column(col, width=140)
        elif col == "Next Follow-Up":
            tree.heading(col, text="Next Follow-Up (MM.DD.YYYY)")
            tree.column(col, width=140)
        else:
            tree.heading(col, text=col)
            tree.column(col, width=100)

    # Scrollbars
    scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Load data from CSV
    load_data(tree, columns)

    # Button bar
    button_frame = ttk.Frame(parent_frame)
    button_frame.pack(fill="x", pady=5)

    ttk.Button(button_frame, text="Add Entry", command=lambda: add_entry(tree, columns)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Edit Entry", command=lambda: edit_entry(tree, columns)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Remove Entry", command=lambda: remove_entry(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Filter by City", command=lambda: filter_entries(tree, columns)).pack(side="left", padx=5)

def load_data(tree, columns):
    """Load or create warm_conversations.csv with the needed columns."""
    if not os.path.exists("warm_conversations.csv"):
        with open("warm_conversations.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
        return

    with open("warm_conversations.csv", "r", newline="") as file:
        reader = csv.reader(file)
        header = next(reader, [])

        # Upgrade CSV if necessary
        missing_cols = [col for col in columns if col not in header]
        if missing_cols:
            combined_header = header + missing_cols
            rows = list(reader)

            with open("warm_conversations.csv", "w", newline="") as fw:
                writer = csv.writer(fw)
                writer.writerow(combined_header)
                writer.writerows(rows)
            header = combined_header

        rows = list(reader)

    for row in rows:
        tree.insert("", "end", values=row)

def save_data(tree, columns):
    """Save data from the TreeView back to warm_conversations.csv."""
    with open("warm_conversations.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row_id in tree.get_children():
            writer.writerow(tree.item(row_id, "values"))

def add_entry(tree, columns):
    """Add a new entry."""
    popup = tk.Toplevel()
    popup.title("Add Warm Conversation")
    popup.geometry("400x400")

    form_cols = [
        "Name",
        "Phone",
        "City",
        "Notes",
        "Status",
        "Priority",
        "Next Follow-Up (MM.DD.YYYY)"
    ]
    entries = []

    for i, label in enumerate(form_cols):
        tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(popup, width=30)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def save_new():
        new_data = [entry.get().strip() for entry in entries]
        if any(not val for val in new_data):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        last_conv = datetime.now().strftime("%m.%d.%Y")
        new_row = new_data[:5] + [last_conv] + [new_data[5]]

        tree.insert("", "end", values=new_row)
        save_data(tree, columns)
        popup.destroy()

    tk.Button(popup, text="Save", command=save_new).grid(row=len(form_cols), column=0, pady=10)
    tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(form_cols), column=1, pady=10)

def edit_entry(tree, columns):
    """Edit an existing entry."""
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "No entry selected for editing!")
        return

    item_id = selected[0]
    old_values = tree.item(item_id, "values")

    popup = tk.Toplevel()
    popup.title("Edit Warm Conversation")
    popup.geometry("400x400")

    form_cols = [
        "Name",
        "Phone",
        "City",
        "Notes",
        "Status",
        "Priority",
        "Next Follow-Up (MM.DD.YYYY)"
    ]
    entries = []

    for i, label in enumerate(form_cols):
        tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(popup, width=30)
        entry.insert(0, old_values[i])
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def save_edit():
        new_data = [entry.get().strip() for entry in entries]
        if any(not val for val in new_data):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        last_conv = datetime.now().strftime("%m.%d.%Y")
        final_values = new_data[:5] + [last_conv] + [new_data[5]]
        tree.item(item_id, values=final_values)
        save_data(tree, columns)
        popup.destroy()

    tk.Button(popup, text="Save", command=save_edit).grid(row=len(form_cols), column=0, pady=10)
    tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(form_cols), column=1, pady=10)

def remove_entry(tree):
    """Remove the selected entry."""
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "No entry selected for removal!")
        return

    if messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this entry?"):
        tree.delete(selected[0])
        save_data(tree, tree["columns"])

def filter_entries(tree, columns):
    """Filter entries by city."""
    popup = tk.Toplevel()
    popup.title("Filter by City")
    popup.geometry("300x150")

    tk.Label(popup, text="Enter City:").grid(row=0, column=0, padx=5, pady=5)
    city_var = tk.StringVar()
    city_entry = tk.Entry(popup, textvariable=city_var, width=20)
    city_entry.grid(row=0, column=1, padx=5, pady=5)

    def apply_filter():
        city_filter = city_var.get().strip().lower()
        for row in tree.get_children():
            values = tree.item(row, "values")
            if city_filter not in values[2].lower():
                tree.detach(row)
            else:
                tree.reattach(row, "", "end")
        popup.destroy()

    def reset_filter():
        for row in tree.get_children():
            tree.delete(row)
        load_data(tree, columns)
        popup.destroy()

    ttk.Button(popup, text="Apply", command=apply_filter).grid(row=1, column=0, padx=5, pady=10)
    ttk.Button(popup, text="Reset", command=reset_filter).grid(row=1, column=1, padx=5, pady=10)
