import tkinter as tk
import json
import random

# Path to the JSON file
JSON_FILE_PATH = "daily_challenges.json"

def load_challenges():
    try:
        with open(JSON_FILE_PATH, "r") as file:
            data = json.load(file)
            print("Loaded Challenges:", data)  # Debugging line
            return data.get("mission_objectives", [])
    except Exception as e:
        print(f"Error loading challenges: {e}")
        return []

def create_conversation_challenges(parent_frame, completed_challenges_list, add_to_completed_listbox):
    challenges = load_challenges()
    available_challenges = [
        {"location": category["location"], "missions": category["missions"]}
        for category in challenges
    ]

    # Ensure a fixed frame size
    parent_frame.config(width=300, height=200)
    parent_frame.pack_propagate(False)

    # Display a message if challenges are not found
    if not available_challenges:
        tk.Label(
            parent_frame,
            text="No challenges found!",
            font=("Helvetica", 16),
            bg="lightblue",
            wraplength=250,
            justify="center",
        ).pack(pady=10)
        return

    # Label to display the current challenge
    current_challenge_label = tk.Label(
        parent_frame,
        text="",
        font=("Helvetica", 14, "bold"),
        wraplength=280,
        bg="lightblue",
        justify="center",
        anchor="center"
    )
    current_challenge_label.pack(expand=True, fill="both", pady=10)

    current_challenge = {"mission": None}  # Store the current challenge persistently

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
                text=f"Location: {location}\n\nMission: {mission}"
            )
            current_challenge["mission"] = mission  # Update current challenge
        else:
            current_challenge_label.config(
                text=f"Location: {location}\nNo missions available."
            )
            current_challenge["mission"] = None

    def complete_challenge():
        mission = current_challenge["mission"]
        if mission:
            print(f"Completing challenge: {mission}")  # Debugging line
            completed_challenges_list.append(mission)
            print(f"Completed Challenges List: {completed_challenges_list}")  # Debugging line
            add_to_completed_listbox(mission)
            current_challenge_label.config(text="Challenge marked as completed!")
            current_challenge["mission"] = None  # Clear the current challenge
        else:
            current_challenge_label.config(text="No challenge to complete!")

    # Button to mark challenges as completed
    complete_button = tk.Button(
        parent_frame,
        text="Mark as Completed",
        command=complete_challenge,
        font=("Helvetica", 10),
    )
    complete_button.pack(pady=5)

    # Button to shuffle the challenges
    shuffle_button = tk.Button(
        parent_frame,
        text="Shuffle Challenge",
        command=update_challenge,
        font=("Helvetica", 10),
    )
    shuffle_button.pack(pady=5)

    # Load the first challenge
    update_challenge()
