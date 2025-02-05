import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import datetime
import random
from textwrap import wrap

# Define BASE_DIR dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Replace hardcoded paths with dynamic ones
fonts_folder = os.path.join(BASE_DIR, "fonts")
save_folder = os.path.join(BASE_DIR, "saved_quotes")
image_folder = os.path.join(BASE_DIR, "images")
quotes_file = os.path.join(BASE_DIR, "quotes.txt")

# Ensure directories exist
os.makedirs(save_folder, exist_ok=True)

# Ensure the save folder exists
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Load quotes from the file
def load_quotes(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Quotes file not found: {file_path}")
        return ["No quotes available. Please check the quotes file."]

quotes = load_quotes(quotes_file)

# Dynamically load all valid image files from the folder
image_files = [
    os.path.join(image_folder, f)
    for f in os.listdir(image_folder)
    if f.endswith(('.png', '.jpg', '.jpeg'))
]

# Dynamically load all valid font files from the fonts folder
font_files = [
    os.path.join(fonts_folder, f)
    for f in os.listdir(fonts_folder)
    if f.endswith(('.ttf', '.otf'))
]

used_images = set()  # To track images that have been used

def get_next_image():
    global used_images
    remaining_images = list(set(image_files) - used_images)

    if not remaining_images:  # Reset the cycle when all images have been used
        used_images.clear()
        remaining_images = image_files

    selected_image = random.choice(remaining_images)
    used_images.add(selected_image)
    return selected_image

def get_random_font():
    """Selects a random font from the fonts folder."""
    if not font_files:
        print("No fonts found in the fonts folder. Using default font.")
        return None
    return random.choice(font_files)

# Function to save the current quote and image
def save_quote(current_image):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = os.path.join(save_folder, f"quote_{timestamp}.png")
    current_image.save(save_path)
    print(f"Quote saved to: {save_path}")

# Function to generate a new quote on an image
def generate_daily_quote(photo_label, custom_quote_entry=None):
    global current_image, current_quote

    if not image_files:
        print("No images found in the folder.")
        return

    # Use custom quote if provided, otherwise select a random quote
    if custom_quote_entry and custom_quote_entry.get().strip():
        current_quote = custom_quote_entry.get().strip()
    else:
        current_quote = random.choice(quotes)

    # Get the next image
    image_path = get_next_image()
    image = Image.open(image_path)

    # Work with a higher resolution for clarity
    max_width, max_height = 1000, 1000
    image = image.resize((max_width, max_height), Image.Resampling.LANCZOS)

    # Prepare to draw text on the image
    draw = ImageDraw.Draw(image)
    wrapped_text = "\n".join(wrap(current_quote, width=30))

    # Adjust font size dynamically based on quote length and image dimensions
    max_font_size = 100
    min_font_size = 20
    font_size = max_font_size
    font_path = get_random_font()

    while font_size >= min_font_size:
        temp_font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=temp_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        if text_width <= image.width * 0.8 and text_height <= image.height * 0.8:
            font = temp_font
            break
        font_size -= 5

    # Center the text on the image
    text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (image.width - text_width) // 2
    y = (image.height - text_height) // 2

    # Add a drop shadow for readability
    shadow_color = "black"
    shadow_offset = 3
    for offset in [(shadow_offset, shadow_offset), (-shadow_offset, -shadow_offset),
                   (shadow_offset, -shadow_offset), (-shadow_offset, shadow_offset)]:
        draw.multiline_text(
            (x + offset[0], y + offset[1]),
            wrapped_text,
            font=font,
            fill=shadow_color,
            align="center"
        )

    # Draw the main text in white
    draw.multiline_text(
        (x, y),
        wrapped_text,
        font=font,
        fill="white",
        align="center"
    )

    # Resize back to display size for the dashboard
    display_width, display_height = 500, 500
    image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

    # Update the global image for saving
    current_image = image

    # Display the image in the GUI
    photo = ImageTk.PhotoImage(image)
    photo_label.config(image=photo)
    photo_label.image = photo

# Function to create the Quote Dashboard
def create_quote_dashboard(parent_frame):
    global current_image, current_quote

    # Photo label to display the image
    photo_label = tk.Label(parent_frame)
    photo_label.pack(pady=10)

    # Entry field for custom quote
    custom_quote_entry = tk.Entry(parent_frame, width=50, font=("Helvetica", 12))
    custom_quote_entry.pack(pady=10)

    # Generate Quote Button
    generate_button = tk.Button(
        parent_frame,
        text="Generate Quote",
        command=lambda: generate_daily_quote(photo_label, custom_quote_entry),
        font=("Helvetica", 12)
    )
    generate_button.pack(pady=10)

    # Save Button
    save_button = tk.Button(
        parent_frame,
        text="Save Quote",
        command=lambda: save_quote(current_image),
        font=("Helvetica", 12)
    )
    save_button.pack(pady=10)

    # Generate the first quote on initialization
    generate_daily_quote(photo_label)

if __name__ == "__main__":
    app = tk.Tk()
    app.title("Quote Dashboard Test")
    app.geometry("600x700")

    # Create a frame for the quote dashboard
    frame = tk.Frame(app, bg="white")
    frame.pack(fill="both", expand=True)

    # Call the create_quote_dashboard function
    create_quote_dashboard(frame)

    app.mainloop()
