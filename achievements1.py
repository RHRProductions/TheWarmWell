import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# File path for persistent storage
ACHIEVEMENTS_FILE = "achievements_data.json"

# Load achievements data
def load_achievements_data():
    if os.path.exists(ACHIEVEMENTS_FILE):
        with open(ACHIEVEMENTS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format in {ACHIEVEMENTS_FILE}")
                return []
    return []

# Save achievements data
def save_achievements_data(data):
    with open(ACHIEVEMENTS_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Global data structure for achievements
achievements_data = load_achievements_data()

print(f"Achievements data loaded: {achievements_data}")  # Debugging line

# Create the Achievements Tracker
def create_achievements_tracker(parent_frame, achievements_data):
    achievements_frame = tk.Frame(parent_frame, bg="white")
    achievements_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # Settings button
    settings_button = tk.Button(achievements_frame, text="Settings", command=lambda: open_settings())
    settings_button.pack(anchor="e", pady=5, padx=5)

    def refresh_dashboard():
        for widget in achievements_frame.winfo_children():
            if widget != settings_button:  # Skip recreating settings_button
                widget.destroy()
        populate_dashboard()

    def increment_progress(achievement):
        """Increment the progress of an achievement."""
        if achievement["current"] < achievement["target"]:
            achievement["current"] += 1
            if achievement["current"] >= achievement["target"]:
                achievement["completed"] = True
                messagebox.showinfo("Achievement Unlocked", f"Reward Unlocked: {achievement['reward']}")
            save_achievements_data(achievements_data)
            refresh_dashboard()

    def populate_dashboard():
        tk.Label(achievements_frame, text="Achievements", bg="white", font=("Helvetica", 14, "bold"))\
            .pack(anchor="w", pady=5)

        for data in achievements_data:
            frame = tk.Frame(achievements_frame, bg="white")
            frame.pack(fill="x", pady=2)

            progress = data["current"] / data["target"] * 100
            unlocked = data["completed"]

            # Achievement task name
            tk.Label(frame, text=data["task"], bg="white", width=20, anchor="w")\
                .grid(row=0, column=0, padx=5)

            # Progress bar
            ttk.Progressbar(frame, value=progress, maximum=100, length=200).grid(row=0, column=1, padx=5)

            # Status
            status = "Unlocked!" if unlocked else f"{data['current']} / {data['target']}"
            tk.Label(frame, text=status, bg="white", width=15, anchor="w")\
                .grid(row=0, column=2, padx=5)

            # Increment button
            increment_button = tk.Button(frame, text="+", width=3, command=lambda a=data: increment_progress(a))
            increment_button.grid(row=0, column=3, padx=5)

    def open_settings():
        """Open the settings menu for achievements."""
        settings_window = tk.Toplevel()
        settings_window.title("Edit Achievements")
        settings_window.geometry("600x400")

        tk.Label(settings_window, text="Edit Achievements", font=("Helvetica", 14, "bold"))\
            .pack(anchor="w", pady=5, padx=10)

        settings_frame = tk.Frame(settings_window)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        entries = []

        def refresh_settings():
            """Repopulate the settings menu with current achievements data."""
            for widget in settings_frame.winfo_children():
                widget.destroy()

            for row, data in enumerate(achievements_data):
                tk.Label(settings_frame, text=f"Achievement {row + 1}:", anchor="w", width=15).grid(row=row, column=0, padx=5, pady=5)

                # Task name entry
                name_entry = tk.Entry(settings_frame, width=20)
                name_entry.insert(0, data["task"])
                name_entry.grid(row=row, column=1, padx=5, pady=5)

                # Target entry
                target_entry = tk.Entry(settings_frame, width=10)
                target_entry.insert(0, str(data["target"]))
                target_entry.grid(row=row, column=2, padx=5, pady=5)

                # Reward entry
                reward_entry = tk.Entry(settings_frame, width=20)
                reward_entry.insert(0, data["reward"])
                reward_entry.grid(row=row, column=3, padx=5, pady=5)

                # Remove button
                remove_button = tk.Button(settings_frame, text="Remove", command=lambda a=data: remove_achievement(a))
                remove_button.grid(row=row, column=4, padx=5, pady=5)

                entries.append((data, name_entry, target_entry, reward_entry))

        def save_changes():
            """Save all changes made in the settings menu."""
            updated_data = []
            for data, name_entry, target_entry, reward_entry in entries:
                try:
                    new_name = name_entry.get().strip()
                    target = int(target_entry.get().strip())
                    reward = reward_entry.get().strip()

                    updated_data.append({
                        "task": new_name,
                        "target": target,
                        "current": data["current"],  # Keep existing progress
                        "reward": reward,
                        "completed": data["completed"]  # Keep existing status
                    })

                except ValueError:
                    messagebox.showerror("Error", "Target must be a number.")
                    return

            achievements_data.clear()
            achievements_data.extend(updated_data)
            save_achievements_data(achievements_data)
            refresh_dashboard()
            settings_window.destroy()

        def add_achievement():
            """Add a new achievement with default values."""
            new_achievement = {
                "task": f"New Achievement {len(achievements_data) + 1}",
                "target": 10,
                "current": 0,
                "reward": "Reward yourself!",
                "completed": False
            }
            achievements_data.append(new_achievement)
            refresh_settings()

        def remove_achievement(achievement):
            """Remove an achievement after confirmation."""
            if messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove the achievement '{achievement['task']}'?"):
                achievements_data.remove(achievement)
                refresh_settings()

        # Add buttons to the settings menu
        tk.Button(settings_window, text="Add Achievement", command=add_achievement).pack(pady=10)
        tk.Button(settings_window, text="Save All", command=save_changes).pack(pady=10)

        refresh_settings()

    # Configure settings button to open the settings menu
    settings_button.config(command=open_settings)

    populate_dashboard()

# Test integration
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Achievement Tracker Test")
    app.geometry("600x400")

    main_frame = tk.Frame(app)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    create_achievements_tracker(main_frame, achievements_data)

    app.protocol("WM_DELETE_WINDOW", lambda: [save_achievements_data(achievements_data), app.destroy()])
    app.mainloop()
