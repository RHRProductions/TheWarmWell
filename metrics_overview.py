import tkinter as tk
from datetime import datetime, timedelta

# Placeholder for lead data
lead_data = [
    {"date": "2025-01-01", "dials": 50, "contacts": 20, "appointments": 5, "appointments_seen": 3, "presentations": 2, "sales": 1, "weekly_income": 1000, "issued_apps": 1},
    {"date": "2025-01-03", "dials": 30, "contacts": 15, "appointments": 4, "appointments_seen": 2, "presentations": 1, "sales": 1, "weekly_income": 800, "issued_apps": 1},
]

# Function to filter data by date range
def filter_data_by_date(data, start_date, end_date):
    return [entry for entry in data if start_date <= datetime.strptime(entry["date"], "%Y-%m-%d") <= end_date]

# Function to calculate totals and averages
def calculate_metrics(data):
    entries = len(data)
    return {
        "dials": sum(entry.get("dials", 0) for entry in data),
        "contacts": sum(entry.get("contacts", 0) for entry in data),
        "appointments": sum(entry.get("appointments", 0) for entry in data),
        "appointments_seen": sum(entry.get("appointments_seen", 0) for entry in data),
        "presentations": sum(entry.get("presentations", 0) for entry in data),
        "sales": sum(entry.get("sales", 0) for entry in data),
        "income": sum(entry.get("weekly_income", 0) for entry in data),
        "issued_apps": sum(entry.get("issued_apps", 0) for entry in data),
        "entries": entries,
    }

# Function to update the metrics display
def update_metrics_display(metrics_label, data, period):
    today = datetime.today()

    # Calculate start and end dates for each period
    if period == "this_week":
        start_date = today - timedelta(days=today.weekday())  # This Monday
        end_date = start_date + timedelta(days=6)  # This Sunday
    elif period == "last_week":
        end_date = today - timedelta(days=today.weekday() + 1)  # Last Sunday
        start_date = end_date - timedelta(days=6)  # Last Monday
    elif period == "this_month":
        start_date = today.replace(day=1)  # First day of this month
        end_date = today  # Today
    elif period == "last_month":
        first_of_this_month = today.replace(day=1)
        last_of_last_month = first_of_this_month - timedelta(days=1)
        start_date = last_of_last_month.replace(day=1)  # First day of last month
        end_date = last_of_last_month  # Last day of last month
    else:
        return

    # Filter data and calculate metrics
    filtered_data = filter_data_by_date(data, start_date, end_date)
    metrics = calculate_metrics(filtered_data)

    # Calculate key ratios
    dials_to_sales_ratio = metrics["sales"] / max(metrics["dials"], 1)  # Avoid division by zero
    income_per_appointment = metrics["income"] / max(metrics["appointments"], 1)
    issued_apps_per_sale = metrics["issued_apps"] / max(metrics["sales"], 1)

    # Update label text
    metrics_label.config(
        text=(
            f"Period: {start_date.strftime('%m-%d-%Y')} to {end_date.strftime('%m-%d-%Y')}\n"
            f"Total Dials: {metrics['dials']}\n"
            f"Total Contacts: {metrics['contacts']}\n"
            f"Total Appointments: {metrics['appointments']}\n"
            f"Total Appointments Seen: {metrics['appointments_seen']}\n"
            f"Total Presentations: {metrics['presentations']}\n"
            f"Total Sales: {metrics['sales']}\n"
            f"Total Income: ${metrics['income']:.2f}\n"
            f"Total Issued Apps: {metrics['issued_apps']}\n\n"
            f"Key Ratios:\n"
            f"Dials-to-Sales Ratio: {dials_to_sales_ratio:.2%}\n"
            f"Income per Appointment: ${income_per_appointment:.2f}\n"
            f"Issued Apps per Sale: {issued_apps_per_sale:.2f}"
        )
    )

# Function to open the edit window
def open_edit_window(parent, data, metrics_label):
    """Opens a popup window for editing previous entries."""
    edit_window = tk.Toplevel(parent)
    edit_window.title("Edit Entries")
    edit_window.geometry("600x400")

    # Listbox to display entries
    listbox = tk.Listbox(edit_window, width=80, height=15, font=("Helvetica", 12))
    listbox.pack(pady=10)

    # Populate listbox with entries
    for i, entry in enumerate(data):
        listbox.insert(tk.END, f"Entry {i + 1}: {entry}")

    def edit_selected_entry():
        """Edit the selected entry."""
        selected_index = listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]

        # Open a new window to edit the selected entry
        entry_editor = tk.Toplevel(edit_window)
        entry_editor.title(f"Edit Entry {index + 1}")
        entry_editor.geometry("400x400")

        # Create fields for each attribute
        fields = {}
        for i, (key, value) in enumerate(data[index].items()):
            tk.Label(entry_editor, text=key, font=("Helvetica", 12)).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            fields[key] = tk.Entry(entry_editor, font=("Helvetica", 12))
            fields[key].insert(0, str(value))
            fields[key].grid(row=i, column=1, padx=10, pady=5)

        def save_changes():
            """Save changes to the selected entry."""
            for key, entry in fields.items():
                if key == "date":
                    data[index][key] = entry.get()
                else:
                    data[index][key] = int(entry.get())
            update_metrics_display(metrics_label, data, "this_week")  # Refresh metrics display
            listbox.delete(index)
            listbox.insert(index, f"Entry {index + 1}: {data[index]}")
            entry_editor.destroy()

        # Save button
        tk.Button(entry_editor, text="Save", command=save_changes, font=("Helvetica", 12)).grid(
            row=len(fields), column=1, pady=20
        )

    def delete_selected_entry():
        """Delete the selected entry."""
        selected_index = listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        del data[index]  # Remove the entry from data
        listbox.delete(index)  # Remove the entry from the listbox
        update_metrics_display(metrics_label, data, "this_week")  # Refresh metrics display

    # Edit button
    edit_button = tk.Button(edit_window, text="Edit Selected", command=edit_selected_entry, font=("Helvetica", 12))
    edit_button.pack(pady=5)

    # Delete button
    delete_button = tk.Button(edit_window, text="Delete Selected", command=delete_selected_entry, font=("Helvetica", 12))
    delete_button.pack(pady=5)

# Function to create metrics overview module
def create_metrics_overview(parent_frame, shared_data):
    global lead_data
    lead_data = shared_data  # Link shared data

    # Frame for metrics overview
    metrics_frame = tk.Frame(parent_frame, bg="white", padx=10, pady=10)
    metrics_frame.pack(fill="both", expand=True)

    # Header
    tk.Label(
        metrics_frame,
        text="Metrics Overview",
        font=("Helvetica", 24, "bold"),
        bg="white",
    ).grid(row=0, column=0, columnspan=3, pady=20)

    # Metrics label
    metrics_label = tk.Label(
        metrics_frame,
        text="No data available.",
        font=("Helvetica", 18),
        bg="white",
        justify="center",
        anchor="center",
    )
    metrics_label.grid(row=1, column=0, columnspan=3, pady=20)

    # Buttons for different time periods
    time_frames = [("This Week", "this_week"), ("Last Week", "last_week"),
                   ("This Month", "this_month"), ("Last Month", "last_month")]

    for i, (label, period) in enumerate(time_frames):
        tk.Button(
            metrics_frame,
            text=label,
            command=lambda p=period: update_metrics_display(metrics_label, lead_data, p),
            font=("Helvetica", 14),
            width=15,
        ).grid(row=2 + i // 2, column=i % 2, padx=10, pady=10)

    # Edit Button
    edit_button = tk.Button(
        metrics_frame,
        text="Edit Entries",
        command=lambda: open_edit_window(parent_frame, lead_data, metrics_label),
        font=("Helvetica", 14),
        width=20,
    )
    edit_button.grid(row=4, column=0, columnspan=3, pady=20)

    # Add column stretching for even spacing
    metrics_frame.grid_columnconfigure(0, weight=1)
    metrics_frame.grid_columnconfigure(1, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Metrics Overview")
    root.geometry("800x600")

    create_metrics_overview(root, lead_data)

    root.mainloop()
