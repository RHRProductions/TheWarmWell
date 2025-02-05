import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import csv
from datetime import datetime

# File path for persistent storage
GOALS_FILE = "goals_data.json"
CSV_FILE = "completed_challenges.csv"

# Load goals data
def load_goals_data():
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format in {GOALS_FILE}")
                return {}
    return {}

# Save goals data
def save_goals_data(goals_data):
    with open(GOALS_FILE, "w") as file:
        json.dump(goals_data, file, indent=4)

# Write to CSV
def log_to_csv(goal_name, reward):
    if not os.path.exists(CSV_FILE):
        # If the file doesn't exist, create it with headers
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date/Time", "Completed Challenges", "Rewards"])

    # Append the new entry
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), goal_name, reward])

# Create the Goals Module
def create_goals_module(parent_frame, goals_data):
    goals_frame = tk.Frame(parent_frame, bg="white")
    goals_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # Settings button
    settings_button = tk.Button(goals_frame, text="Settings")
    settings_button.pack(anchor="e", pady=5, padx=5)

    goal_widgets = {}  # Store references to widgets for direct updates

    def increment_goal(task_name):
        goal = goals_data[task_name]
        if goal["current"] < goal["target"]:
            goal["current"] += 1
            progress = goal["current"] / goal["target"] * 100

            # Update progress bar and status directly
            goal_widgets[task_name]["progress"].config(value=progress)
            status_text = "Completed!" if goal["current"] >= goal["target"] else f"{goal['current']} / {goal['target']}"
            goal_widgets[task_name]["status"].config(text=status_text)

            if goal["current"] >= goal["target"] and not goal["completed"]:
                goal["completed"] = True
                messagebox.showinfo("Goal Completed!", f"Reward Unlocked: {goal['reward']}")

                # Log the completed goal to the CSV file
                log_to_csv(task_name, goal["reward"])

            # Save progress without refreshing the entire dashboard
            save_goals_data(goals_data)

    def populate_dashboard():
        for widget in goals_frame.winfo_children():
            if widget != settings_button:
                widget.destroy()

        tk.Label(goals_frame, text="Goals", bg="white", font=("Helvetica", 14, "bold"))\
            .pack(anchor="w", pady=5)

        for task_name, goal in goals_data.items():
            frame = tk.Frame(goals_frame, bg="white")
            frame.pack(fill="x", pady=2)

            # Goal name
            tk.Label(frame, text=task_name, bg="white", width=20, anchor="w")\
                .grid(row=0, column=0, padx=5)

            # Progress bar
            progress = goal["current"] / goal["target"] * 100
            progress_bar = ttk.Progressbar(frame, value=progress, maximum=100, length=200)
            progress_bar.grid(row=0, column=1, padx=5)

            # Status
            status_text = "Completed!" if goal["completed"] else f"{goal['current']} / {goal['target']}"
            status_label = tk.Label(frame, text=status_text, bg="white", width=15, anchor="w")
            status_label.grid(row=0, column=2, padx=5)

            # Increment button
            increment_button = tk.Button(frame, text="+", width=3, command=lambda task=task_name: increment_goal(task))
            increment_button.grid(row=0, column=3, padx=5)

            # Save widget references for updates
            goal_widgets[task_name] = {
                "progress": progress_bar,
                "status": status_label,
            }

    # Initial population
    populate_dashboard()

    def open_settings():
        # Settings window for editing goals
        settings_window = tk.Toplevel()
        settings_window.title("Edit Goals")
        settings_window.geometry("600x400")

        tk.Label(settings_window, text="Edit Goals", font=("Helvetica", 14, "bold"))\
            .pack(anchor="w", pady=5, padx=10)

        settings_frame = tk.Frame(settings_window)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        entries = {}

        def refresh_settings():
            # Clear and repopulate settings frame
            for widget in settings_frame.winfo_children():
                widget.destroy()

            for row, (task_name, goal) in enumerate(goals_data.items()):
                tk.Label(settings_frame, text=f"Task {row + 1}:", anchor="w", width=15).grid(row=row, column=0, padx=5, pady=5)

                # Task name entry
                name_entry = tk.Entry(settings_frame, width=20)
                name_entry.insert(0, task_name)
                name_entry.grid(row=row, column=1, padx=5, pady=5)

                # Target entry
                target_entry = tk.Entry(settings_frame, width=10)
                target_entry.insert(0, str(goal["target"]))
                target_entry.grid(row=row, column=2, padx=5, pady=5)

                # Reward entry
                reward_entry = tk.Entry(settings_frame, width=20)
                reward_entry.insert(0, goal["reward"])
                reward_entry.grid(row=row, column=3, padx=5, pady=5)

                # Remove button
                remove_button = tk.Button(settings_frame, text="Remove", command=lambda task=task_name: remove_goal(task))
                remove_button.grid(row=row, column=4, padx=5, pady=5)

                entries[task_name] = (name_entry, target_entry, reward_entry)

        def save_changes():
            updated_goals = {}
            for old_task_name, (name_entry, target_entry, reward_entry) in entries.items():
                try:
                    new_task_name = name_entry.get().strip()
                    target = int(target_entry.get().strip())
                    reward = reward_entry.get().strip()

                    if new_task_name:
                        updated_goals[new_task_name] = {
                            "target": target,
                            "current": goals_data[old_task_name]["current"],
                            "reward": reward,
                            "completed": goals_data[old_task_name]["completed"],
                        }

                except ValueError:
                    messagebox.showerror("Error", "Target must be a number.")
                    return

            # Update and save data
            goals_data.clear()
            goals_data.update(updated_goals)
            save_goals_data(goals_data)

            # Repopulate dashboard with updated data
            populate_dashboard()
            settings_window.destroy()

        def add_goal():
            new_task_name = f"New Goal {len(goals_data) + 1}"
            goals_data[new_task_name] = {"target": 10, "current": 0, "reward": "Reward yourself!", "completed": False}
            refresh_settings()

        def remove_goal(task_name):
            if messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove the goal '{task_name}'?"):
                del goals_data[task_name]
                refresh_settings()

        tk.Button(settings_window, text="Add Goal", command=add_goal).pack(pady=10)
        tk.Button(settings_window, text="Save All", command=save_changes).pack(pady=10)

        refresh_settings()

    settings_button.config(command=open_settings)

# Test integration
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Goals Module Test")
    app.geometry("600x400")

    main_frame = tk.Frame(app)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    test_goals_data = load_goals_data()
    if not test_goals_data:
        test_goals_data = {
            "Example Goal": {"target": 10, "current": 0, "reward": "Reward yourself!", "completed": False}
        }

    create_goals_module(main_frame, test_goals_data)

    app.protocol("WM_DELETE_WINDOW", lambda: [save_goals_data(test_goals_data), app.destroy()])
    app.mainloop()
