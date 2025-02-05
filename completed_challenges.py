import tkinter as tk
import csv
import os

# Path to save completed challenges
COMPLETED_CHALLENGES_CSV = "completed_challenges.csv"

def save_to_csv(completed_challenges_list):
    try:
        with open(COMPLETED_CHALLENGES_CSV, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Completed Challenges"])
            for challenge in completed_challenges_list:
                writer.writerow([challenge])
        print(f"Completed challenges saved to {COMPLETED_CHALLENGES_CSV}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def create_completed_challenges(parent_frame, completed_challenges_list):
    parent_frame.config(width=300, height=200)
    parent_frame.pack_propagate(False)

    tk.Label(
        parent_frame,
        text="Completed Challenges",
        font=("Helvetica", 14),
        bg="white",
        anchor="center"
    ).pack(pady=5)

    # Listbox to display completed challenges
    listbox = tk.Listbox(parent_frame, font=("Helvetica", 10), bg="white", height=10)
    listbox.pack(fill="both", expand=True, pady=5)

    # Add existing completed challenges on initialization
    for challenge in completed_challenges_list:
        listbox.insert("end", challenge)

    # Function to add items to the listbox dynamically
    def add_to_completed_listbox(item):
        print(f"Adding to listbox: {item}")  # Debugging: Log each item being added
        listbox.insert("end", item)

    # Save Progress Button
    save_button = tk.Button(
        parent_frame,
        text="Save Progress",
        command=lambda: save_to_csv(completed_challenges_list),
        font=("Helvetica", 10)
    )
    save_button.pack(pady=5)

    # Return the dynamic add function for external calls
    return add_to_completed_listbox
