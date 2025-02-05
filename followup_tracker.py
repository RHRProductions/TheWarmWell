import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import csv
import os

# File paths for persistent storage
FOLLOW_UP_FILE = "follow_up_data.json"
CLIENTS_FILE = "clients.csv"
DEAD_LEADS_FILE = "dead_leads.csv"

# Define follow-up data globally
follow_up_data = []

# Load follow-up data from JSON file
def load_follow_up_data():
    global follow_up_data
    if os.path.exists(FOLLOW_UP_FILE):
        with open(FOLLOW_UP_FILE, "r") as file:
            follow_up_data.extend(json.load(file))
        print("Follow-up data loaded successfully:", follow_up_data)

# Save follow-up data to JSON file
def save_follow_up_data():
    with open(FOLLOW_UP_FILE, "w") as file:
        json.dump(follow_up_data, file, indent=4)
    print("Follow-up data saved successfully.")

# Append data to a CSV file
def append_to_csv(file_path, data):
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Name", "Date", "Notes", "Status"])
        writer.writerow([data["name"], data["date"], data["notes"], data["status"]])

# Create the Follow-Up Tracker
def create_follow_up_tracker(parent_frame):
    tracker_frame = tk.Frame(parent_frame, bg="white")
    tracker_frame.pack(fill="both", expand=True)

    # Treeview for displaying follow-ups
    columns = ("Name", "Follow-Up Date", "Notes", "Status")
    tree = ttk.Treeview(tracker_frame, columns=columns, show="headings", height=6)
    tree.pack(fill="x", expand=True, padx=5, pady=5)

    # Add vertical scrollbar for the treeview
    vsb = ttk.Scrollbar(tracker_frame, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)

    # Define column headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    # Populate treeview with data
    def refresh_treeview():
        for item in tree.get_children():
            tree.delete(item)
        for lead in follow_up_data:
            tree.insert("", "end", values=(lead["name"], lead["date"], lead["notes"], lead["status"]))

    refresh_treeview()

    # Entry fields and buttons
    control_frame = tk.Frame(tracker_frame, bg="white")
    control_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(control_frame, text="Name:", bg="white").grid(row=0, column=0, padx=1, pady=1)
    name_entry = tk.Entry(control_frame, width=15)
    name_entry.grid(row=0, column=1, padx=1, pady=1)

    tk.Label(control_frame, text="Date (MM.DD.YYYY):", bg="white").grid(row=0, column=2, padx=1, pady=1)
    date_entry = tk.Entry(control_frame, width=15)
    date_entry.grid(row=0, column=3, padx=1, pady=1)

    tk.Label(control_frame, text="Notes:", bg="white").grid(row=0, column=4, padx=1, pady=1)
    notes_entry = tk.Entry(control_frame, width=20)
    notes_entry.grid(row=0, column=5, padx=1, pady=1)

    def validate_date_format(date_text):
        try:
            datetime.strptime(date_text, "%m.%d.%Y")
            return True
        except ValueError:
            return False

    def add_follow_up():
        name = name_entry.get()
        date = date_entry.get()
        notes = notes_entry.get()
        if not name or not date or not notes:
            messagebox.showerror("Error", "All fields are required!")
            return
        if not validate_date_format(date):
            messagebox.showerror("Error", "Date must be in MM.DD.YYYY format!")
            return

        new_follow_up = {"name": name, "date": date, "notes": notes, "status": "Pending"}
        follow_up_data.append(new_follow_up)
        save_follow_up_data()
        refresh_treeview()
        name_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        notes_entry.delete(0, tk.END)
        refresh_dropdown()

    tk.Button(control_frame, text="Add Follow-Up", command=add_follow_up).grid(row=0, column=6, padx=5, pady=5)

    # Update status section
    tk.Label(control_frame, text="Select Lead:", bg="white").grid(row=1, column=0, padx=1, pady=1)
    selected_item_var = tk.StringVar()
    dropdown = ttk.Combobox(control_frame, textvariable=selected_item_var, state="readonly")
    dropdown.grid(row=1, column=1, padx=1, pady=1)

    tk.Label(control_frame, text="Status:", bg="white").grid(row=1, column=2, padx=1, pady=1)
    status_var = tk.StringVar()
    status_dropdown = ttk.Combobox(control_frame, textvariable=status_var, values=["Pending", "Contacted", "Overdue", "Sold", "Dead"], state="readonly")
    status_dropdown.grid(row=1, column=3, padx=1, pady=1)

    def refresh_dropdown():
        dropdown["values"] = [tree.item(child)["values"][0] for child in tree.get_children()]

    refresh_dropdown()

    def update_status():
        selected_name = selected_item_var.get()
        new_status = status_var.get()
        if selected_name and new_status:
            for child in tree.get_children():
                item = tree.item(child)
                if item["values"][0] == selected_name:
                    tree.item(child, values=(item["values"][0], item["values"][1], item["values"][2], new_status))
                    break

            for entry in follow_up_data:
                if entry["name"] == selected_name:
                    entry["status"] = new_status
                    if new_status in ["Sold", "Dead"]:
                        follow_up_data.remove(entry)
                        save_follow_up_data()
                        refresh_treeview()
                        if new_status == "Sold":
                            append_to_csv(CLIENTS_FILE, entry)
                        elif new_status == "Dead":
                            append_to_csv(DEAD_LEADS_FILE, entry)
                    break

            selected_item_var.set("")
            status_var.set("")
            refresh_dropdown()
        else:
            messagebox.showerror("Error", "Please select a lead and a status to update!")

    tk.Button(control_frame, text="Update Status", command=update_status).grid(row=1, column=4, padx=5, pady=5)

if __name__ == "__main__":
    load_follow_up_data()
    app = tk.Tk()
    app.title("Follow-Up Tracker")
    app.geometry("800x600")

    follow_up_tracker_frame = tk.Frame(app)
    follow_up_tracker_frame.pack(fill="both", expand=True)

    create_follow_up_tracker(follow_up_tracker_frame)

    app.protocol("WM_DELETE_WINDOW", lambda: [save_follow_up_data(), app.destroy()])
    app.mainloop()
