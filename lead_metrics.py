from tkinter import ttk, messagebox
import tkinter as tk
import datetime
import json
import os

# File for persistent storage
DATA_FILE = "lead_data.json"

# Initialize lead_data
lead_data = []

# Load data from file
def load_data():
    global lead_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            lead_data = json.load(file)
        print("Data loaded successfully:", lead_data)  # Debugging
    else:
        print("No existing data file found. Starting fresh.")  # Debugging

# Save data to file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(lead_data, file, indent=4)

# Function to clear all data
def clear_all_data(update_summary_callback):
    global lead_data
    if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all data? This action cannot be undone."):
        lead_data.clear()
        save_data()
        update_summary_callback()
        messagebox.showinfo("Data Cleared", "All data has been cleared successfully.")

# Function to create the Lead Metrics Module
def create_lead_metrics(parent_frame, shared_data):
    global lead_data
    lead_data = shared_data  # Link shared data

    # Main Frame
    main_frame = tk.Frame(parent_frame, bg="white")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Header
    tk.Label(main_frame, text="Lead Metrics", font=("Helvetica", 18, "bold"), bg="white").pack(pady=10)

    # Metrics Frames
    metrics_frame = tk.Frame(main_frame, bg="white")
    metrics_frame.pack(fill="x", pady=10)

    # Call Days Section
    call_days_frame = tk.Frame(metrics_frame, bg="lightgray", pady=10, padx=10)
    call_days_frame.pack(side="left", fill="both", expand=True, padx=5)

    tk.Label(call_days_frame, text="Call Days Metrics", font=("Helvetica", 14), bg="lightgray").pack(pady=5)
    call_fields = [("Dials", "dials_entry"), ("Contacts", "contacts_entry"), ("Appointments Set", "appointments_entry")]
    call_entries = {}
    for label_text, var_name in call_fields:
        tk.Label(call_days_frame, text=f"{label_text}:", font=("Helvetica", 12), bg="lightgray").pack(anchor="w", pady=2)
        entry = tk.Entry(call_days_frame, width=15)
        entry.pack(anchor="w", pady=2)
        call_entries[var_name] = entry
    tk.Button(call_days_frame, text="Add Call Metrics", command=lambda: add_call_metrics(call_entries), font=("Helvetica", 12)).pack(pady=5)

    # Field Days Section
    field_days_frame = tk.Frame(metrics_frame, bg="lightgray", pady=10, padx=10)
    field_days_frame.pack(side="right", fill="both", expand=True, padx=5)

    tk.Label(field_days_frame, text="Field Days Metrics", font=("Helvetica", 14), bg="lightgray").pack(pady=5)
    field_fields = [("Appointments Seen", "appointments_seen_entry"), ("Presentations Made", "presentations_entry"), ("Sales", "sales_entry")]
    field_entries = {}
    for label_text, var_name in field_fields:
        tk.Label(field_days_frame, text=f"{label_text}:", font=("Helvetica", 12), bg="lightgray").pack(anchor="w", pady=2)
        entry = tk.Entry(field_days_frame, width=15)
        entry.pack(anchor="w", pady=2)
        field_entries[var_name] = entry
    tk.Button(field_days_frame, text="Add Field Metrics", command=lambda: add_field_metrics(field_entries), font=("Helvetica", 12)).pack(pady=5)

    # Weekly Metrics Section
    weekly_frame = tk.Frame(main_frame, bg="white", pady=10)
    weekly_frame.pack(fill="x", pady=10)

    tk.Label(weekly_frame, text="Weekly Metrics", font=("Helvetica", 14), bg="white").pack(pady=5)
    tk.Label(weekly_frame, text="Weekly Income:", font=("Helvetica", 12), bg="white").pack(anchor="w", pady=2)
    weekly_income_entry = tk.Entry(weekly_frame, width=15)
    weekly_income_entry.pack(anchor="w", pady=2)
    tk.Label(weekly_frame, text="Issued Apps:", font=("Helvetica", 12), bg="white").pack(anchor="w", pady=2)
    issued_apps_entry = tk.Entry(weekly_frame, width=15)
    issued_apps_entry.pack(anchor="w", pady=2)
    tk.Button(weekly_frame, text="Add Weekly Metrics", command=lambda: add_weekly_metrics(weekly_income_entry, issued_apps_entry), font=("Helvetica", 12)).pack(pady=5)

    # Summary Section
    summary_frame = tk.Frame(main_frame, bg="white", pady=10)
    summary_frame.pack(fill="x", pady=10)

    global summary_label
    summary_label = tk.Label(summary_frame, text="Totals will appear here.", font=("Helvetica", 12), bg="white", justify="center")
    summary_label.pack()

    # Clear Data Button
    tk.Button(main_frame, text="Clear All Data", command=lambda: clear_all_data(update_summary), font=("Helvetica", 12), bg="red", fg="white").pack(pady=10)

    # Functions
    def add_call_metrics(entries):
        lead_data.append({
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "dials": int(entries["dials_entry"].get()),
            "contacts": int(entries["contacts_entry"].get()),
            "appointments": int(entries["appointments_entry"].get()),
            "appointments_seen": 0,
            "presentations": 0,
            "sales": 0,
            "weekly_income": 0,
            "issued_apps": 0,
        })
        save_data()
        update_summary()
        for entry in entries.values():
            entry.delete(0, "end")

    def add_field_metrics(entries):
        lead_data.append({
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "dials": 0,
            "contacts": 0,
            "appointments": 0,
            "appointments_seen": int(entries["appointments_seen_entry"].get()),
            "presentations": int(entries["presentations_entry"].get()),
            "sales": int(entries["sales_entry"].get()),
            "weekly_income": 0,
            "issued_apps": 0,
        })
        save_data()
        update_summary()
        for entry in entries.values():
            entry.delete(0, "end")

    def add_weekly_metrics(income_entry, apps_entry):
        try:
            lead_data.append({
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "dials": 0,
                "contacts": 0,
                "appointments": 0,
                "appointments_seen": 0,
                "presentations": 0,
                "sales": 0,
                "weekly_income": float(income_entry.get()),
                "issued_apps": int(apps_entry.get()),
            })
            save_data()
            update_summary()
            income_entry.delete(0, "end")
            apps_entry.delete(0, "end")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for Weekly Income and Issued Apps.")

    def update_summary():
        total_dials = sum(item.get("dials", 0) for item in lead_data)
        total_contacts = sum(item.get("contacts", 0) for item in lead_data)
        total_appointments = sum(item.get("appointments", 0) for item in lead_data)
        total_appointments_seen = sum(item.get("appointments_seen", 0) for item in lead_data)
        total_presentations = sum(item.get("presentations", 0) for item in lead_data)
        total_sales = sum(item.get("sales", 0) for item in lead_data)
        total_income = sum(item.get("weekly_income", 0) for item in lead_data)
        total_issued_apps = sum(item.get("issued_apps", 0) for item in lead_data)

        summary_label.config(
            text=(
                f"Total Dials: {total_dials}\n"
                f"Total Contacts: {total_contacts}\n"
                f"Total Appointments Set: {total_appointments}\n"
                f"Total Appointments Seen: {total_appointments_seen}\n"
                f"Total Presentations Made: {total_presentations}\n"
                f"Total Sales: {total_sales}\n"
                f"Total Weekly Income: ${total_income:.2f}\n"
                f"Total Issued Apps: {total_issued_apps}"
            )
        )

# Load data at startup
load_data()
