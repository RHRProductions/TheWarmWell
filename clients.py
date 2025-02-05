import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv
from datetime import datetime

class ClientOutreachModule:
    def __init__(self, parent):
        self.expected_columns = [
            "Name",
            "Phone",
            "City",
            "Notes",
            "Status",
            "Priority",
            "Last Contact",
            "Contact Frequency"
        ]

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.frame, columns=self.expected_columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        for col in self.expected_columns:
            if col == "Last Contact":
                self.tree.heading(col, text="Last Contact (MM.DD.YYYY)")
                self.tree.column(col, width=130)
            else:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)

        self.scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)

        self.load_data()

        self.button_frame = ttk.Frame(parent)
        self.button_frame.pack(fill="x", pady=5)

        ttk.Button(self.button_frame, text="Add Entry", command=self.add_entry).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Remove Entry", command=self.remove_entry).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Update Status", command=self.update_status).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Filter by City", command=self.apply_filter).pack(side="left", padx=5)

    def load_data(self):
        if not os.path.exists("clients.csv"):
            with open("clients.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.expected_columns)
            return

        with open("clients.csv", "r", newline='') as file:
            reader = csv.reader(file)
            header = next(reader, [])
            rows = list(reader)

        for row_data in rows:
            self.tree.insert("", "end", values=row_data)

    def save_table(self):
        with open("clients.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.expected_columns)
            for row_id in self.tree.get_children():
                writer.writerow(self.tree.item(row_id, "values"))

    def add_entry(self):
        popup = tk.Toplevel(self.frame)
        popup.title("Add Entry")
        popup.geometry("400x350")

        form_cols = [
            "Name",
            "Phone",
            "City",
            "Notes",
            "Status",
            "Priority",
            "Contact Frequency"
        ]
        entries = []

        for i, label in enumerate(form_cols):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if label == "Status":
                options = ["Pending", "Follow-Up Scheduled", "Needs Info", "Active", "Closed"]
                var = tk.StringVar()
                cb = ttk.Combobox(popup, textvariable=var, values=options, state="readonly")
                cb.grid(row=i, column=1, padx=5, pady=5)
                entries.append(var)
            elif label == "Priority":
                options = ["High", "Medium", "Low"]
                var = tk.StringVar()
                cb = ttk.Combobox(popup, textvariable=var, values=options, state="readonly")
                cb.grid(row=i, column=1, padx=5, pady=5)
                entries.append(var)
            elif label == "Contact Frequency":
                options = ["Annually", "Bi-Annually", "Quarterly", "Monthly"]
                var = tk.StringVar()
                cb = ttk.Combobox(popup, textvariable=var, values=options, state="readonly")
                cb.grid(row=i, column=1, padx=5, pady=5)
                entries.append(var)
            else:
                entry = tk.Entry(popup, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries.append(entry)

        def save_new_entry():
            row_data = [widget.get().strip() for widget in entries]
            if any(not value for value in row_data):
                messagebox.showerror("Error", "All fields must be filled!")
                return

            today_str = datetime.now().strftime("%m.%d.%Y")
            final_values = [
                row_data[0], row_data[1], row_data[2], row_data[3],
                row_data[4], row_data[5], today_str, row_data[6]
            ]

            self.tree.insert("", "end", values=final_values)
            self.save_table()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_new_entry).grid(row=len(form_cols), column=0, pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(form_cols), column=1, pady=10)

    def remove_entry(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "No entry selected for removal!")
            return

        confirm = messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this entry?")
        if confirm:
            self.tree.delete(sel[0])
            self.save_table()

    def update_status(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "No entry selected to update!")
            return

        item_id = sel[0]
        values = self.tree.item(item_id, "values")
        popup = tk.Toplevel(self.frame)
        popup.title("Update Status")
        popup.geometry("300x200")

        tk.Label(popup, text=f"Update Status for: {values[0]}").pack(pady=10)
        status_var = tk.StringVar()
        status_dropdown = ttk.Combobox(popup, textvariable=status_var, values=["Pending", "Follow-Up Scheduled", "Needs Info", "Active", "Closed"], state="readonly")
        status_dropdown.pack(pady=10)

        def save_status_update():
            new_status = status_var.get()
            if not new_status:
                messagebox.showerror("Error", "Please select a new status!")
                return

            updated_values = list(values)
            updated_values[4] = new_status
            self.tree.item(item_id, values=updated_values)
            self.save_table()
            popup.destroy()

        tk.Button(popup, text="Save", command=save_status_update).pack(pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=10)

    def apply_filter(self):
        popup = tk.Toplevel(self.frame)
        popup.title("Filter by City")
        popup.geometry("300x250")

        tk.Label(popup, text="Enter City to Filter:").pack(pady=10)
        city_var = tk.StringVar()
        city_entry = tk.Entry(popup, textvariable=city_var)
        city_entry.pack(pady=10)

        def apply_filter():
            city = city_var.get().strip().lower()
            if not city:
                messagebox.showerror("Error", "City cannot be empty!")
                return

            filtered_entries = [
                self.tree.item(child, "values")
                for child in self.tree.get_children()
                if self.tree.item(child, "values")[2].strip().lower() == city
            ]

            for child in self.tree.get_children():
                self.tree.delete(child)

            for entry in filtered_entries:
                self.tree.insert("", "end", values=entry)

        def reset_filter():
            for child in self.tree.get_children():
                self.tree.delete(child)
            self.load_data()

        tk.Button(popup, text="Apply Filter", command=apply_filter).pack(pady=10)
        tk.Button(popup, text="Reset Filter", command=reset_filter).pack(pady=10)
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

def create_client_outreach_module(tab):
    ClientOutreachModule(tab)
