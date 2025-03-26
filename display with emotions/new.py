#display with emotions/new.py
import os
import sys
import time
import logging
import threading
import glob
import re
import signal
from queue import Queue
import spidev as SPI
from PIL import Image

# Add path for LCD library
sys.path.append("..")
from lib import LCD_2inch

# Configure logging
logging.basicConfig(level=logging.INFO)

class RobotEmotionsLCD:
    def __init__(self):
        # LCD configuration - from test.py
        self.RST = 27
        self.DC = 25
        self.BL = 18
        self.bus = 0
        self.device = 0
        
        # Core state management - from file.py
        self.current_state = None
        self.command_queue = Queue()
        self.running = True
        
        # Dictionary to store frame paths for each emotion
        self.emotion_frames = {
            'bootup': [], 'bootup3': [], 'neutral': [], 'angry': [],
            'blink': [], 'blink2': [], 'dizzy': [], 'excited': [],
            'happy': [], 'happy2': [], 'happy3': [], 'sad': [], 'sleep': []
        }

        # Frame rates for each emotion (fps)
        self.emotion_speeds = {
            'bootup': 20, 'bootup3': 20, 'neutral': 20, 'angry': 60,
            'blink': 40, 'blink2': 40, 'dizzy': 90, 'excited': 10,
            'happy': 20, 'happy2': 20, 'happy3': 20, 'sad': 20, 'sleep': 15
        }
        
        # Speed settings
        self.transition_speed = 60  # Speed for transitioning from neutral (fps)
        
        # Initialize signal handler and load frames
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def initialize_lcd(self):
        """Initialize the LCD display"""
        try:
            self.disp = LCD_2inch.LCD_2inch()
            self.disp.Init()
            self.disp.clear()
            self.disp.bl_DutyCycle(50)  # Set backlight brightness to 50%
            logging.info("LCD initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize LCD: {e}")
            return False
    
    def natural_sort_key(self, s):
        """
        Generate a key for natural sorting of strings containing numbers.
        Ensures "frame2.png" comes before "frame10.png"
        """
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', s)]

    def load_sorted_frames(self):
        """
        Load and sort frames for each emotion based on frame number.
        Uses natural sorting to ensure correct frame sequence.
        """
        for emotion in self.emotion_frames:
            # Get and sort all PNG files in the emotion directory
            try:
                frames = sorted(glob.glob(f"{emotion}/frame*.png"), key=self.natural_sort_key)
                self.emotion_frames[emotion] = frames
                logging.info(f"Loaded {len(frames)} frames for {emotion}")
            except Exception as e:
                logging.error(f"Error loading frames for {emotion}: {e}")
                self.emotion_frames[emotion] = []

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logging.info("\nExiting program...")
        self.running = False
        if hasattr(self, 'disp'):
            try:
                self.disp.module_exit()
            except:
                pass
        sys.exit(0)

    def display_frame(self, frame_path):
        """
        Display a frame on the LCD.
        Loads image, rotates it, and shows it on LCD.
        """
        try:
            # Load the image
            image = Image.open(frame_path)
            
            # Rotate the image 180 degrees (as in test.py)
            image = image.rotate(180)
            
            # Display the image on the LCD
            self.disp.ShowImage(image)
            return True
        except Exception as e:
            logging.error(f"Error displaying frame {frame_path}: {e}")
            return False

    def play_frames(self, frames, emotion, is_transition=False):
        """
        Play frames for an emotion with specified timing on LCD.
        
        Args:
            frames: List of frame paths to play
            emotion: Name of the emotion being played
            is_transition: Whether this is a transition from neutral state
        """
        if not frames:
            logging.warning(f"No frames found for emotion: {emotion}")
            return
            
        # Calculate delay based on emotion or transition speed
        speed = self.transition_speed if is_transition else self.emotion_speeds[emotion]
        delay = 1.0 / speed  # Convert fps to seconds
        
        # Determine if emotion should loop (only neutral and sleep loop)
        should_loop = emotion in ['sleep', 'neutral'] and not is_transition
        
        while self.running:
            for frame_path in frames:
                if not self.running:
                    return
                
                # Check for new commands during playback
                if not self.command_queue.empty():
                    return
                
                # Display frame on LCD
                self.display_frame(frame_path)
                time.sleep(delay)
            
            # For non-looping emotions, hold last frame briefly then exit
            if not should_loop:
                time.sleep(0.5)  # Hold last frame for 500ms
                return
            
            # For looping emotions, check if we should continue
            if not should_loop or not self.running or not self.command_queue.empty():
                return

    def play_sleep_loop(self):
        """Handle sleep state with continuous animation"""
        self.current_state = 'sleep'
        while self.running and self.current_state == 'sleep':
            if not self.command_queue.empty():
                self.command_queue.get()  # Any input wakes from sleep
                self.current_state = 'neutral'
                return
            
            self.play_frames(self.emotion_frames['sleep'], 'sleep')
            if not self.running or not self.command_queue.empty():
                self.current_state = 'neutral'
                return

    def play_emotion(self, emotion, is_transition=False):
        """Play an emotion animation"""
        frames = self.emotion_frames[emotion]
        self.play_frames(frames, emotion, is_transition)

    def play_neutral_loop(self):
        """
        Main loop for neutral state.
        Handles emotion transitions and command processing.
        """
        self.current_state = 'neutral'
        while self.running and self.current_state == 'neutral':
            if not self.command_queue.empty():
                command = self.command_queue.get().strip()
                if command:  # Ignore empty commands
                    if command in ['angry', 'blink', 'blink2', 'dizzy', 'excited', 
                                 'happy', 'happy2', 'happy3', 'sad']:
                        # Play accelerated neutral transition
                        self.play_emotion('neutral', is_transition=True)
                        # Play requested emotion
                        self.play_emotion(command)
                        self.current_state = 'neutral'
                        continue
                    
                    elif command == 'sleep':
                        self.play_sleep_loop()
                        continue
                    
                    elif command == 'bootup3':
                        self.play_emotion('bootup3')
                        self.current_state = 'neutral'
                        continue
                    
                    elif command in ['exit', 'quit']:
                        self.running = False
                        return

            # Continue neutral animation loop
            self.play_frames(self.emotion_frames['neutral'], 'neutral')
            if not self.running or not self.command_queue.empty():
                continue

    def command_listener(self):
        """Thread to handle user input commands"""
        while self.running:
            try:
                command = input().lower().strip()
                self.command_queue.put(command)
                if command in ['exit', 'quit']:
                    self.running = False
                    break
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break

    def run(self):
        """Initialize and run the robot emotions on LCD display"""
        # Initialize LCD
        if not self.initialize_lcd():
            logging.error("Failed to initialize LCD. Exiting.")
            return
            
        # Load emotion frames
        self.load_sorted_frames()
        
        # Start command listener in separate thread
        listener_thread = threading.Thread(target=self.command_listener)
        listener_thread.daemon = True
        listener_thread.start()

        # Display available commands
        print("\nAvailable commands:")
        print("- boot: Start the robot")
        print("- angry: Show angry emotion")
        print("- blink/blink2: Show blink animations")
        print("- dizzy: Show dizzy emotion")
        print("- excited: Show excited emotion")
        print("- happy/happy2/happy3: Show happy animations")
        print("- sad: Show sad emotion")
        print("- sleep: Enter sleep mode")
        print("- bootup3: Show alternate boot animation")
        print("- exit/quit: Exit program")
        print("\nWaiting for boot command...")

        # Main program loop
        try:
            while self.running:
                if not self.command_queue.empty():
                    command = self.command_queue.get().strip()
                    if command == 'boot':
                        self.play_emotion('bootup')
                        self.play_neutral_loop()
                    elif command in ['exit', 'quit']:
                        break
        finally:
            # Cleanup on exit
            self.running = False
            if hasattr(self, 'disp'):
                try:
                    self.disp.clear()
                    self.disp.module_exit()
                    logging.info("Display cleared and exited")
                except:
                    pass
            sys.exit(0)

if __name__ == "__main__":
    robot = RobotEmotionsLCD()
    robot.run()
