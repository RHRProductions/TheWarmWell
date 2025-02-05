import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv

# File paths for persistent storage
T65_FILE = "warm_t65_leads.csv"
ISSUED_T65_FILE = "issued_t65_leads.csv"
DEAD_T65_FILE = "dead_t65_leads.csv"

# Global data for Warm T65s
warm_t65_data = []

def load_warm_t65_data():
    global warm_t65_data
    warm_t65_data.clear()
    
    if not os.path.exists(T65_FILE):
        print("Warm T65s file not found, starting with an empty list.")
        return
    
    with open(T65_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if all(key in row for key in ["Name", "Phone", "City", "Notes", "Status", "Priority"]):
                warm_t65_data.append(row)
            else:
                print("Invalid row format in CSV:", row)
    
    print("Warm T65s data loaded successfully.")

def save_warm_t65_data():
    with open(T65_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Phone", "City", "Notes", "Status", "Priority"])
        writer.writeheader()
        writer.writerows(warm_t65_data)

def create_warm_t65s_module(parent_frame):
    frame = ttk.Frame(parent_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create the table
    tree = ttk.Treeview(frame, columns=("Name", "Phone", "City", "Notes", "Status", "Priority"), show="headings")
    tree.pack(fill="both", expand=True)

    # Define headings
    for col in ("Name", "Phone", "City", "Notes", "Status", "Priority"):
        tree.heading(col, text=col)
        tree.column(col, width=100, stretch=True)

    # Add scrollbars
    scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)

    def refresh_treeview():
        tree.delete(*tree.get_children())
        for entry in warm_t65_data:
            tree.insert("", "end", values=(entry["Name"], entry["Phone"], entry["City"],
                                         entry["Notes"], entry["Status"], entry["Priority"]))

    def add_entry():
        popup = tk.Toplevel(parent_frame)
        popup.title("Add Entry")
        popup.geometry("400x350")

        labels = ["Name", "Phone", "City", "Notes", "Status", "Priority"]
        entries = {}

        status_options = ["Follow-Up", "Appointment Set", "Pending", "Issued", "Dead"]
        priority_options = ["High", "Medium", "Low"]

        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label == "Status":
                var = tk.StringVar()
                dropdown = ttk.Combobox(popup, textvariable=var, values=status_options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = var
            elif label == "Priority":
                var = tk.StringVar()
                dropdown = ttk.Combobox(popup, textvariable=var, values=priority_options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = var
            else:
                entry = tk.Entry(popup, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = entry

        def save_new_entry():
            new_entry = {label: entries[label].get() if isinstance(entries[label], tk.StringVar)
                        else entries[label].get() for label in labels}
            
            if any(not value.strip() for value in new_entry.values()):
                messagebox.showerror("Error", "All fields must be filled!")
                return

            if new_entry["Status"] in ["Issued", "Dead"]:
                target_file = ISSUED_T65_FILE if new_entry["Status"] == "Issued" else DEAD_T65_FILE
                with open(target_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=new_entry.keys())
                    if os.path.getsize(target_file) == 0:
                        writer.writeheader()
                    writer.writerow(new_entry)
                messagebox.showinfo("Success", f"Lead added directly to {new_entry['Status'].lower()}_t65_leads.csv")
            else:
                warm_t65_data.append(new_entry)
                save_warm_t65_data()
                refresh_treeview()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_new_entry).grid(row=len(labels), column=0, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, pady=10)

    def edit_entry():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an entry to edit.")
            return

        selected_values = tree.item(selected_item[0])['values']
        selected_index = warm_t65_data.index(next(
            entry for entry in warm_t65_data
            if all(str(value) == str(selected_values[i])
                  for i, value in enumerate(entry.values()))
        ))

        popup = tk.Toplevel(parent_frame)
        popup.title("Edit Entry")
        popup.geometry("400x350")

        labels = ["Name", "Phone", "City", "Notes", "Status", "Priority"]
        entries = {}

        status_options = ["Follow-Up", "Appointment Set", "Pending", "Issued", "Dead"]
        priority_options = ["High", "Medium", "Low"]

        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label == "Status":
                var = tk.StringVar(value=selected_values[4])
                dropdown = ttk.Combobox(popup, textvariable=var, values=status_options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = var
            elif label == "Priority":
                var = tk.StringVar(value=selected_values[5])
                dropdown = ttk.Combobox(popup, textvariable=var, values=priority_options, state="readonly")
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = var
            else:
                entry = tk.Entry(popup, width=30)
                entry.insert(0, selected_values[i])
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries[label] = entry

        def save_edited_entry():
            edited_entry = {label: entries[label].get() if isinstance(entries[label], tk.StringVar)
                          else entries[label].get() for label in labels}
            
            if any(not value.strip() for value in edited_entry.values()):
                messagebox.showerror("Error", "All fields must be filled!")
                return

            if edited_entry["Status"] in ["Issued", "Dead"]:
                # Move to appropriate file
                target_file = ISSUED_T65_FILE if edited_entry["Status"] == "Issued" else DEAD_T65_FILE
                with open(target_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=edited_entry.keys())
                    if os.path.getsize(target_file) == 0:
                        writer.writeheader()
                    writer.writerow(edited_entry)
                # Remove from warm leads
                warm_t65_data.pop(selected_index)
                messagebox.showinfo("Success",
                    f"Lead has been moved to {edited_entry['Status'].lower()}_t65_leads.csv and removed from warm leads.")
            else:
                warm_t65_data[selected_index] = edited_entry
            
            save_warm_t65_data()
            refresh_treeview()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_edited_entry).grid(row=len(labels), column=0, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, pady=10)

    def update_status():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an entry to update status.")
            return

        selected_values = tree.item(selected_item[0])['values']
        selected_index = warm_t65_data.index(next(
            entry for entry in warm_t65_data
            if all(str(value) == str(selected_values[i])
                  for i, value in enumerate(entry.values()))
        ))

        popup = tk.Toplevel(parent_frame)
        popup.title("Update Status")
        popup.geometry("300x150")

        tk.Label(popup, text="New Status:").pack(pady=5)
        status_var = tk.StringVar(value=selected_values[4])
        status_options = ["Follow-Up", "Appointment Set", "Pending", "Issued", "Dead"]
        status_dropdown = ttk.Combobox(popup, textvariable=status_var, values=status_options, state="readonly")
        status_dropdown.pack(pady=5)

        def save_status():
            new_status = status_var.get()
            lead_to_move = warm_t65_data[selected_index].copy()
            
            if new_status in ["Dead", "Issued"]:
                # Move to appropriate file
                target_file = ISSUED_T65_FILE if new_status == "Issued" else DEAD_T65_FILE
                with open(target_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=lead_to_move.keys())
                    if os.path.getsize(target_file) == 0:
                        writer.writeheader()
                    writer.writerow(lead_to_move)
                # Remove from warm leads
                warm_t65_data.pop(selected_index)
                messagebox.showinfo("Success",
                    f"Lead has been moved to {new_status.lower()}_t65_leads.csv and removed from warm leads.")
            else:
                # Just update the status
                warm_t65_data[selected_index]["Status"] = new_status

            save_warm_t65_data()
            refresh_treeview()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_status).pack(pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)

    def filter_entries():
        popup = tk.Toplevel(parent_frame)
        popup.title("Filter by City")
        popup.geometry("300x150")

        # Get unique cities from the data
        cities = sorted(list(set(entry["City"] for entry in warm_t65_data)))
        cities.insert(0, "All")  # Add "All" option at the beginning

        tk.Label(popup, text="Select City:").pack(pady=5)
        city_var = tk.StringVar(value="All")
        city_dropdown = ttk.Combobox(popup, textvariable=city_var, values=cities, state="readonly")
        city_dropdown.pack(pady=5)

        def apply_filter():
            selected_city = city_var.get()
            tree.delete(*tree.get_children())
            
            for entry in warm_t65_data:
                if selected_city == "All" or entry["City"] == selected_city:
                    tree.insert("", "end", values=(entry["Name"], entry["Phone"], entry["City"],
                                                 entry["Notes"], entry["Status"], entry["Priority"]))
            popup.destroy()

        tk.Button(popup, text="Apply Filter", command=apply_filter).pack(pady=10)
        tk.Button(popup, text="Clear Filter", command=lambda: [refresh_treeview(), popup.destroy()]).pack(pady=5)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)

    # Initial data load
    load_warm_t65_data()
    refresh_treeview()

    # Entry fields and buttons
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill="x", pady=5)

    ttk.Button(button_frame, text="Add Entry", command=add_entry).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Edit Entry", command=edit_entry).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Update Status", command=update_status).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Filter", command=filter_entries).pack(side="left", padx=5)

    refresh_treeview()

    return frame  # Return the frame for potential future use
