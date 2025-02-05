import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import csv

# File paths for persistent storage
PRESENTED_FILE = "presented_data.json"
CONVERTED_PRESENTED_FILE = "converted_presented.csv"
NOT_INTERESTED_PRESENTED_FILE = "not_interested_presented.csv"

# Global data for presented prospects
presented_data = []

# Load presented data from JSON file
def load_presented_data():
    global presented_data
    presented_data.clear()  # Clear the list to prevent duplication
    if os.path.exists(PRESENTED_FILE):
        with open(PRESENTED_FILE, "r") as file:
            presented_data.extend(json.load(file))
        print("Presented data loaded successfully.")
    else:
        print("Presented data file not found, starting with an empty list.")

# Save presented data to JSON file
def save_presented_data():
    with open(PRESENTED_FILE, "w") as file:
        json.dump(presented_data, file, indent=4)

# Append data to a CSV file
def append_to_csv(file_path, data):
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Name", "Phone", "City", "Notes", "Status", "Priority"])
        writer.writerow([data["name"], data["phone"], data["city"], data["notes"], data["status"], data["priority"]])

# Create the Presented Prospects Module
def create_presented_module(parent_frame):
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

    # Populate treeview with data
    def refresh_treeview(data=None):
        for item in tree.get_children():
            tree.delete(item)
        display_data = data if data else presented_data
        for entry in display_data:
            tree.insert("", "end", values=(
                entry["name"],
                entry["phone"],
                entry["city"],
                entry["notes"],
                entry["status"],
                entry["priority"]
            ))

    # Initial load of data
    refresh_treeview()

    # Entry fields and buttons
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill="x", pady=5)

    def add_entry():
        popup = tk.Toplevel(parent_frame)
        popup.title("Add Entry")
        popup.geometry("400x350")

        labels = ["Name", "Phone", "City", "Notes", "Status", "Priority"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label in ["Status", "Priority"]:
                options = ["Pending Decision", "Follow-Up Scheduled", "Needs More Information"] if label == "Status" else ["High", "Medium", "Low"]
                var = tk.StringVar()
                dropdown = ttk.Combobox(popup, textvariable=var, values=options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries.append(var)
            else:
                entry = tk.Entry(popup, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries.append(entry)

        def save_new_entry():
            new_entry = {
                "name": entries[0].get(),
                "phone": entries[1].get(),
                "city": entries[2].get(),
                "notes": entries[3].get(),
                "status": entries[4].get(),
                "priority": entries[5].get(),
            }

            if any(not value.strip() for value in new_entry.values()):
                messagebox.showerror("Error", "All fields must be filled!")
                return

            presented_data.append(new_entry)
            save_presented_data()
            refresh_treeview()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_new_entry).grid(row=len(labels), column=0, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, pady=10)

    ttk.Button(button_frame, text="Add Entry", command=add_entry).pack(side="left", padx=5)

    def edit_entry():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No entry selected for editing!")
            return

        item_id = selected_item[0]
        values = tree.item(item_id, "values")

        popup = tk.Toplevel(parent_frame)
        popup.title("Edit Entry")
        popup.geometry("400x350")

        labels = ["Name", "Phone", "City", "Notes", "Status", "Priority"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label in ["Status", "Priority"]:
                options = ["Pending Decision", "Follow-Up Scheduled", "Needs More Information"] if label == "Status" else ["High", "Medium", "Low"]
                var = tk.StringVar(value=values[i])
                dropdown = ttk.Combobox(popup, textvariable=var, values=options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries.append(var)
            else:
                entry = tk.Entry(popup, width=30)
                entry.insert(0, values[i])
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries.append(entry)

        def save_edited_entry():
            updated_entry = {
                "name": entries[0].get(),
                "phone": entries[1].get(),
                "city": entries[2].get(),
                "notes": entries[3].get(),
                "status": entries[4].get(),
                "priority": entries[5].get(),
            }

            if any(not value.strip() for value in updated_entry.values()):
                messagebox.showerror("Error", "All fields must be filled!")
                return

            for entry in presented_data:
                if (
                    entry["name"] == values[0] and
                    entry["phone"] == values[1] and
                    entry["city"] == values[2]
                ):
                    presented_data.remove(entry)
                    break

            presented_data.append(updated_entry)
            save_presented_data()
            refresh_treeview()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_edited_entry).grid(row=len(labels), column=0, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, pady=10)

    ttk.Button(button_frame, text="Edit Entry", command=edit_entry).pack(side="left", padx=5)

    def update_status():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No entry selected to update!")
            return

        item_id = selected_item[0]
        values = tree.item(item_id, "values")

        popup = tk.Toplevel(parent_frame)
        popup.title("Update Status")
        popup.geometry("300x200")

        tk.Label(popup, text="Update Status for: " + values[0]).pack(pady=10)

        status_var = tk.StringVar()
        status_dropdown = ttk.Combobox(popup, textvariable=status_var, values=["Pending Decision", "Follow-Up Scheduled", "Needs More Information", "Converted", "Not Interested"], state="readonly")
        status_dropdown.pack(pady=10)

        def save_status_update():
            new_status = status_var.get()
            if not new_status:
                messagebox.showerror("Error", "Please select a new status!")
                return

            for entry in presented_data:
                if (
                    entry["name"] == values[0] and
                    entry["phone"] == values[1] and
                    entry["city"] == values[2]
                ):
                    entry["status"] = new_status

                    if new_status in ["Converted", "Not Interested"]:
                        presented_data.remove(entry)
                        append_to_csv(
                            CONVERTED_PRESENTED_FILE if new_status == "Converted" else NOT_INTERESTED_PRESENTED_FILE,
                            entry
                        )
                    break

            save_presented_data()
            refresh_treeview()
            popup.destroy()

        ttk.Button(popup, text="Save", command=save_status_update).pack(pady=10)
        ttk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=10)

    ttk.Button(button_frame, text="Update Status", command=update_status).pack(side="left", padx=5)

    def filter_by_city():
        popup = tk.Toplevel(parent_frame)
        popup.title("Filter by City")
        popup.geometry("300x250")

        tk.Label(popup, text="Enter City to Filter:").pack(pady=10)
        city_var = tk.StringVar()
        city_entry = tk.Entry(popup, textvariable=city_var)
        city_entry.pack(pady=10)

        def apply_filter():
            city_to_filter = city_var.get().strip().lower()
            if not city_to_filter:
                messagebox.showerror("Error", "City cannot be empty!")
                return

            filtered_entries = [
                entry for entry in presented_data if entry["city"].strip().lower() == city_to_filter
            ]

            refresh_treeview(filtered_entries)

        def reset_filter():
            refresh_treeview()

        ttk.Button(popup, text="Apply Filter", command=apply_filter).pack(pady=10)
        ttk.Button(popup, text="Reset Filter", command=reset_filter).pack(pady=10)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    ttk.Button(button_frame, text="Filter by City", command=filter_by_city).pack(side="left", padx=5)

    load_presented_data()
    refresh_treeview()
