import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import platform

# ChromeOS display settings
if platform.system() == "Linux":
    os.environ['DISPLAY'] = ':0'
    os.environ['TKROOT'] = ''
    os.environ['TK_LIBRARY'] = '/usr/lib/x86_64-linux-gnu/tk8.6'

# Import sync manager for Google Drive sync
from sync_manager import SyncManager

# Import modules for various dashboard functionalities
from lead_metrics import create_lead_metrics
from quote_dashboard import create_quote_dashboard
from metrics_overview import create_metrics_overview
from visualization import create_visualization
from callchallenges import create_call_challenges
from completed_challenges import create_completed_challenges
from followup_tracker import create_follow_up_tracker, load_follow_up_data, save_follow_up_data
from referral_tracker import create_referrals_tracker, load_referrals_data, save_referrals_data
from achievements1 import create_achievements_tracker, save_achievements_data, achievements_data
from goals1 import create_goals_module, save_goals_data, load_goals_data
from presented import create_presented_module, load_presented_data, save_presented_data  # Updated

# Import other modules
from no_shows import create_no_shows_module
from at_risk import create_deals_at_risk_module
from warm_life_leads import create_warm_life_leads_module
from warm_t65s import create_warm_t65s_module
from connectors import create_community_connectors_module
from clients import create_client_outreach_module

# Initialize sync manager
sync_manager = SyncManager()
try:
    print("Starting sync manager...")
    sync_manager.start_sync()
    print("Sync manager started successfully")
except Exception as e:
    print(f"Error starting sync manager: {e}")

# Debugging toggle
DEBUG = True
def debug_print(*args):
    if DEBUG:
        print(*args)

# Set base directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
debug_print("Base Directory:", BASE_DIR)

# File paths for persistent storage (use BASE_DIR for portability)
DATA_FILE = os.path.join(BASE_DIR, "lead_data.json")

# Global lead data
lead_data = []

# Load data from file
def load_data():
    global lead_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            lead_data.extend(json.load(file))
        debug_print("Lead data loaded successfully:", lead_data)

# Save data to file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(lead_data, file, indent=4)
    debug_print("Lead data saved successfully.")

debug_print("Current Working Directory:", os.getcwd())

# GUI Initialization
try:
    print("Starting GUI initialization...")
    app = tk.Tk()
    print("Tk instance created...")
    
    # Set window properties
    app.title("Daily Dashboard")
    app.geometry("1800x900")
    print("Window geometry set...")
    
    # Ensure window is visible and active
    app.update_idletasks()
    app.deiconify()
    app.focus_force()
    print("Window focus forced...")
    
    # Wait for window to be ready
    app.after(1000, lambda: app.attributes('-zoomed', True))
    app.after(1000, lambda: print("Window maximized..."))
    
    # Keep window on top until fully initialized
    app.attributes('-topmost', True)
    app.after(2000, lambda: app.attributes('-topmost', False))
    
except Exception as e:
    print(f"Error initializing GUI: {e}")
    raise

# Add these lines right after GUI initialization
app.update()
print("Initial update complete...")
    
# Load data before starting the app
load_data()
load_follow_up_data()
load_referrals_data()
load_presented_data()  # Load presented data
raw_goals_data = load_goals_data()

debug_print("Raw goals data loaded:", raw_goals_data)
goals_data = raw_goals_data
debug_print("Final goals data:", goals_data)

# Set up main canvas and layout
main_canvas = tk.Canvas(app)
main_canvas.pack(side="left", fill="both", expand=True)

scrollbar_y = tk.Scrollbar(app, orient="vertical", command=main_canvas.yview)
scrollbar_y.pack(side="right", fill="y")

scrollbar_x = tk.Scrollbar(app, orient="horizontal", command=main_canvas.xview)
scrollbar_x.pack(side="bottom", fill="x")

main_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

dash_frame = tk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=dash_frame, anchor="nw")

def update_scroll_region(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

dash_frame.bind("<Configure>", update_scroll_region)

###############################################################################
# Mouse wheel scrolling logic (GLOBAL binding)
###############################################################################
def _on_mousewheel(event):
    """Handle mouse-wheel on Windows/macOS."""
    system_name = platform.system()
    if system_name == "Darwin":
        main_canvas.yview_scroll(int(-event.delta), "units")
    else:
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_mousewheel_linux(event):
    """Handle mouse-wheel on Linux (<Button-4> and <Button-5>)."""
    if event.num == 4:
        main_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        main_canvas.yview_scroll(1, "units")

# Bind to the entire application so scrolling works anywhere in the window
app.bind_all("<MouseWheel>", _on_mousewheel)       # Windows/macOS
app.bind_all("<Button-4>", _on_mousewheel_linux)   # Linux scroll up
app.bind_all("<Button-5>", _on_mousewheel_linux)   # Linux scroll down
###############################################################################

# Create individual modules (top rows)
quote_frame = tk.Frame(dash_frame, bg="white", width=250, height=150)
quote_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

metrics_frame = tk.Frame(dash_frame, bg="white", width=250, height=150)
metrics_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

visualization_frame = tk.Frame(dash_frame, bg="white", width=400, height=150)
visualization_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

daily_metrics_frame = tk.Frame(dash_frame, bg="white", width=400, height=150)
daily_metrics_frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

daily_challenges_frame = tk.Frame(dash_frame, bg="lightblue", width=250, height=150)
daily_challenges_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

completed_challenges_frame = tk.Frame(dash_frame, bg="white", width=250, height=150)
completed_challenges_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

achievements_tracker_frame = tk.Frame(dash_frame, bg="white", width=250, height=150)
achievements_tracker_frame.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

goals_tracker_frame = tk.Frame(dash_frame, bg="white", width=250, height=150)
goals_tracker_frame.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")

# Create a Notebook to hold tabs for all modules
notebook = ttk.Notebook(dash_frame)
notebook.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

# Create tabs for each module (in the specified order)
presented_tab = ttk.Frame(notebook)  # Tab 1
notebook.add(presented_tab, text="Presented")

warm_t65s_tab = ttk.Frame(notebook)  # Tab 2
notebook.add(warm_t65s_tab, text="Warm T65s")

warm_life_leads_tab = ttk.Frame(notebook)  # Tab 3
notebook.add(warm_life_leads_tab, text="Warm Life Leads")

no_shows_tab = ttk.Frame(notebook)  # Tab 4
notebook.add(no_shows_tab, text="No-Shows/Cancellations")

save_a_deal_tab = ttk.Frame(notebook)  # Tab 5
notebook.add(save_a_deal_tab, text="Save A Deal")

connectors_tab = ttk.Frame(notebook)  # Tab 6
notebook.add(connectors_tab, text="Connectors")

referrals_tab = ttk.Frame(notebook)  # Tab 7
notebook.add(referrals_tab, text="Referrals")

clients_tab = ttk.Frame(notebook)  # Tab 8
notebook.add(clients_tab, text="Clients")

# Initialize all modules in the specified order
try:
    add_to_completed_listbox = create_completed_challenges(completed_challenges_frame, [])
    create_call_challenges(
        daily_challenges_frame,
        completed_call_challenges_list=[],
        add_to_completed_listbox=add_to_completed_listbox
    )
    create_quote_dashboard(quote_frame)
    create_metrics_overview(metrics_frame, lead_data)
    create_visualization(visualization_frame, lead_data)
    create_lead_metrics(daily_metrics_frame, lead_data)
    create_achievements_tracker(achievements_tracker_frame, achievements_data)
    create_goals_module(goals_tracker_frame, goals_data)

    # Initialize each tab module
    create_presented_module(presented_tab)  # Tab 1
    create_warm_t65s_module(warm_t65s_tab)  # Tab 2
    create_warm_life_leads_module(warm_life_leads_tab)  # Tab 3
    create_no_shows_module(no_shows_tab)  # Tab 4
    create_deals_at_risk_module(save_a_deal_tab)  # Tab 5
    create_community_connectors_module(connectors_tab)  # Tab 6
    create_referrals_tracker(referrals_tab)  # Tab 7
    create_client_outreach_module(clients_tab)  # Tab 8

except Exception as e:
    print(f"Error initializing dashboard modules: {e}")

# Save data on close
def on_closing():
    try:
        print("Starting shutdown sequence...")
        sync_manager.stop_sync()
        print("Sync manager stopped...")
        sync_manager.force_sync()
        print("Final sync completed...")
        save_data()
        save_follow_up_data()
        save_referrals_data()
        save_presented_data()
        save_achievements_data(achievements_data)
        save_goals_data(goals_data)
        print("All data saved...")
        app.destroy()
    except Exception as e:
        print(f"Error during shutdown: {e}")
        # Force close if there's an error
        app.quit()

app.protocol("WM_DELETE_WINDOW", on_closing)

# Keep window open
def check_window():
    if app.winfo_exists():
        app.after(100, check_window)
    else:
        print("Window closed unexpectedly")

app.after(100, check_window)
app.mainloop()