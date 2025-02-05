import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_visualization(parent_frame, shared_data):
    # Debugging print
    print("Data passed to Visualization Module:", shared_data)

    # Extract data for visualization
    dates = [item["date"] for item in shared_data]
    dials = [item["dials"] for item in shared_data]
    contacts = [item["contacts"] for item in shared_data]
    appointments = [item["appointments"] for item in shared_data]
    sales = [item["sales"] for item in shared_data]
    income = [item["weekly_income"] for item in shared_data]
    issued_apps = [item.get("issued_apps", 0) for item in shared_data]  # Default to 0 if not present

    # Debugging print for extracted data
    print("Extracted Dates:", dates)
    print("Dials:", dials)
    print("Contacts:", contacts)
    print("Appointments:", appointments)
    print("Sales:", sales)
    print("Income:", income)
    print("Issued Apps:", issued_apps)

    # Create a Figure and Axes
    figure = Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)

    # Function to redraw the graph based on selected checkboxes
    def redraw_graph():
        ax.clear()  # Clear the existing graph
        if dials_var.get():
            ax.plot(dates, dials, label="Dials", marker="o")
        if contacts_var.get():
            ax.plot(dates, contacts, label="Contacts", marker="o")
        if appointments_var.get():
            ax.plot(dates, appointments, label="Appointments", marker="o")
        if sales_var.get():
            ax.plot(dates, sales, label="Sales", marker="o")
        if income_var.get():
            ax.plot(dates, income, label="Income ($)", marker="o", linestyle="--")
        if issued_apps_var.get():
            ax.plot(dates, issued_apps, label="Issued Apps", marker="o", linestyle="-.")

        # Configure the chart
        ax.set_title("Performance Over Time", fontsize=14, weight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Count / Income ($)", fontsize=12)
        ax.legend()
        ax.grid(True, which="major", linestyle="--", alpha=0.5)

        # Rotate date labels for better readability
        ax.tick_params(axis="x", rotation=45)

        # Redraw the canvas
        canvas.draw()

    # Create Tkinter variables for checkboxes
    dials_var = tk.BooleanVar(value=True)
    contacts_var = tk.BooleanVar(value=True)
    appointments_var = tk.BooleanVar(value=True)
    sales_var = tk.BooleanVar(value=True)
    income_var = tk.BooleanVar(value=True)
    issued_apps_var = tk.BooleanVar(value=True)

    # Create checkboxes
    controls_frame = tk.Frame(parent_frame)
    controls_frame.pack(fill="x", pady=5)

    tk.Checkbutton(controls_frame, text="Dials", variable=dials_var, command=redraw_graph).pack(side="left")
    tk.Checkbutton(controls_frame, text="Contacts", variable=contacts_var, command=redraw_graph).pack(side="left")
    tk.Checkbutton(controls_frame, text="Appointments", variable=appointments_var, command=redraw_graph).pack(side="left")
    tk.Checkbutton(controls_frame, text="Sales", variable=sales_var, command=redraw_graph).pack(side="left")
    tk.Checkbutton(controls_frame, text="Income", variable=income_var, command=redraw_graph).pack(side="left")
    tk.Checkbutton(controls_frame, text="Issued Apps", variable=issued_apps_var, command=redraw_graph).pack(side="left")

    # Add the chart to the Tkinter frame
    canvas = FigureCanvasTkAgg(figure, parent_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Draw the initial graph
    redraw_graph()
