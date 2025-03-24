import os
import time
import tkinter as tk
from PIL import Image, ImageTk

# Define the frame count for each emotion
frame_count = {
    'angry': 20, 
    'blink': 39, 
    'blink2': 20,
    'bootup': 120,
    'bootup3': 124, 
    'dizzy': 67, 
    'excited': 24, 
    'happy': 45, 
    'happy2': 20, 
    'happy3': 26, 
    'neutral': 61, 
    'sad': 47, 
    'sleep': 112
}

# Function to display the selected emotion
def show_emotion(emotion):
    global current_emotion, running  # Global variables to manage state

    if running:
        running = False  # Stop any ongoing animation
        root.after_cancel(current_emotion)  # Cancel the current scheduled animation
    
    # Clear the current list of frames
    frames = []
    emotion_dir = os.path.join('emotions', emotion)

    # Load frames for the selected emotion
    for i in range(frame_count[emotion]):
        frame_path = os.path.join(emotion_dir, f'frame{i}.png')
        if os.path.exists(frame_path):
            frames.append(ImageTk.PhotoImage(Image.open(frame_path)))
        else:
            print(f"Warning: {frame_path} not found, skipping this frame.")
    
    def update_frame(frame_index):
        if running and frames:
            label.config(image=frames[frame_index])
            frame_index = (frame_index + 1) % len(frames)
            current_emotion = root.after(50, update_frame, frame_index)  # Schedule the next frame

    # Start the new animation
    running = True
    update_frame(0)

# Function to handle option menu selection
def on_select(event):
    emotion = option_var.get()
    show_emotion(emotion)

# Set up the main GUI window
root = tk.Tk()
root.title("Emotion Display")

# Create a label to display the images
label = tk.Label(root)
label.pack()

# Create an option menu to select emotions
option_var = tk.StringVar(root)
emotions_list = list(frame_count.keys())
option_var.set(emotions_list[0])  # Set default option

option_menu = tk.OptionMenu(root, option_var, *emotions_list, command=on_select)
option_menu.pack()

# Global variables to manage the animation loop
running = False
current_emotion = None

# Initial display of the default emotion
show_emotion(option_var.get())

# Start the main event loop
root.mainloop()
