import tkinter as tk
import json
import random

CALL_JSON_FILE_PATH = "call_challenges.json"
DAILY_JSON_FILE_PATH = "daily_challenges.json"

current_json_file_path = CALL_JSON_FILE_PATH
challenges = []

def load_challenges():
    global challenges
    try:
        with open(current_json_file_path, "r") as file:
            data = json.load(file)
            challenges = data.get("mission_objectives", [])
            return challenges
    except Exception as e:
        print(f"Error loading challenges: {e}")
        challenges = []
        return []

def create_call_challenges(parent_frame, completed_call_challenges_list, add_to_completed_listbox):
    global current_json_file_path, challenges
    challenges = load_challenges()

    # Outer container for scrollability
    outer_container = tk.Frame(parent_frame, bg="lightblue")
    outer_container.pack(fill="both", expand=True, padx=10, pady=10)

    # Scrollbars
    canvas = tk.Canvas(outer_container, bg="lightblue", highlightthickness=0)
    scrollbar_y = tk.Scrollbar(outer_container, orient="vertical", command=canvas.yview)
    scrollbar_x = tk.Scrollbar(outer_container, orient="horizontal", command=canvas.xview)
    content_frame = tk.Frame(canvas, bg="lightblue")

    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Pack the canvas and scrollbars
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")

    # Configure dynamic resizing
    def resize_content(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    content_frame.bind("<Configure>", resize_content)

    # Display message if challenges are not found
    if not challenges:
        tk.Label(
            content_frame,
            text="No call challenges found!",
            font=("Helvetica", 16),
            bg="lightblue",
            wraplength=250,
            justify="center",
        ).pack(pady=10)
        return

    # Label to display the current challenge
    current_challenge_label = tk.Label(
        content_frame,
        text="",
        font=("Helvetica", 14, "bold"),
        wraplength=250,
        bg="lightblue",
        justify="center",
        anchor="center",
    )
    current_challenge_label.pack(fill="both", pady=10)

    current_challenge = {"mission": None}

    def update_challenge():
        if not challenges:
            current_challenge_label.config(text="No more challenges available!")
            current_challenge["mission"] = None
            return
        category = random.choice(challenges)
        location = category.get("location", "Unknown Location")
        missions = category.get("missions", [])
        if missions:
            mission = random.choice(missions)
            current_challenge_label.config(
                text=f"📍 Location: {location}\n\n🎯 Mission: {mission}"
            )
            current_challenge["mission"] = mission
        else:
            current_challenge_label.config(
                text=f"📍 Location: {location}\nNo missions available."
            )
            current_challenge["mission"] = None

    def complete_challenge():
        mission = current_challenge["mission"]
        if mission:
            completed_call_challenges_list.append(mission)
            add_to_completed_listbox(mission)
            current_challenge_label.config(text="✅ Challenge marked as completed!")
            current_challenge["mission"] = None
        else:
            current_challenge_label.config(text="No challenge to complete!")

    def change_json_file(selected_file):
        global current_json_file_path, challenges
        current_json_file_path = selected_file
        challenges = load_challenges()
        update_challenge()

    # Dropdown menu for JSON file selection
    menu_var = tk.StringVar(value="Call Challenges")
    menu = tk.OptionMenu(
        content_frame,
        menu_var,
        "Call Challenges",
        "Daily Challenges",
        command=lambda selected: change_json_file(
            CALL_JSON_FILE_PATH if selected == "Call Challenges" else DAILY_JSON_FILE_PATH
        ),
    )
    menu.config(font=("Helvetica", 10), width=20)
    menu.pack(pady=5)

    # Buttons
    tk.Button(
        content_frame,
        text="Mark as Completed",
        command=complete_challenge,
        font=("Helvetica", 10),
        width=20,
    ).pack(pady=5)

    tk.Button(
        content_frame,
        text="Shuffle Challenge",
        command=update_challenge,
        font=("Helvetica", 10),
        width=20,
    ).pack(pady=5)

    # Load the first challenge
    update_challenge()

# Test integration
if __name__ == "__main__":
    def add_to_completed_listbox(mission):
        print(f"Added to completed listbox: {mission}")

    completed_challenges = []

    root = tk.Tk()
    root.title("Call Challenges Test")
    root.geometry("600x400")

    test_frame = tk.Frame(root, bg="lightblue")
    test_frame.pack(fill="both", expand=True, padx=10, pady=10)

    create_call_challenges(test_frame, completed_challenges, add_to_completed_listbox)

    root.mainloop()
