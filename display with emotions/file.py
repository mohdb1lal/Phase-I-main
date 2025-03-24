import cv2
import os
import glob
import threading
from queue import Queue
import time
import numpy as np
import signal
import sys
import re

class RobotEmotions:
    def __init__(self):
        # Core state management
        self.current_state = None
        self.command_queue = Queue()
        self.running = True
        
        # Display settings
        self.frame_width = 200
        self.frame_height = 150
        self.target_screen_height = 200  # Desired display height
        
        # Speed settings
        self.transition_speed = 60  # Speed for transitioning from neutral (fps)
        
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
        
        # Initialize signal handler and load frames
        signal.signal(signal.SIGINT, self.signal_handler)
        self.load_sorted_frames()
        
        # Pre-calculate display dimensions
        self.screen_width = int(self.target_screen_height * (self.frame_width / self.frame_height))

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
        found_dimensions = False
        for emotion in self.emotion_frames:
            # Get and sort all PNG files in the emotion directory
            frames = sorted(glob.glob(f"{emotion}/frame*.png"), key=self.natural_sort_key)
            self.emotion_frames[emotion] = frames
            print(f"Loaded {len(frames)} frames for {emotion}")
            
            # Get dimensions from first valid frame
            if not found_dimensions and frames:
                test_frame = cv2.imread(frames[0])
                if test_frame is not None:
                    self.frame_height, self.frame_width = test_frame.shape[:2]
                    found_dimensions = True

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\nExiting program...")
        self.running = False
        cv2.destroyAllWindows()
        sys.exit(0)

    def load_frame(self, frame_path):
        """
        Load and resize a frame for display.
        Uses pre-calculated dimensions for efficiency.
        """
        frame = cv2.imread(frame_path)
        if frame is not None:
            return cv2.resize(frame, (self.screen_width, self.target_screen_height))
        return None

    def play_frames(self, frames, emotion, is_transition=False):
        """
        Play frames for an emotion with specified timing.
        
        Args:
            frames: List of frame paths to play
            emotion: Name of the emotion being played
            is_transition: Whether this is a transition from neutral state
        """
        # Calculate delay based on emotion or transition speed
        speed = self.transition_speed if is_transition else self.emotion_speeds[emotion]
        delay = int(1000 / speed)  # Convert fps to milliseconds
        
        # Determine if emotion should loop (only neutral and sleep loop)
        should_loop = emotion in ['sleep', 'neutral'] and not is_transition
        
        while self.running:
            for frame_path in frames:
                if not self.running:
                    return
                
                # Check for new commands during playback
                if not self.command_queue.empty():
                    return
                
                # Load and display frame
                frame = self.load_frame(frame_path)
                if frame is not None:
                    cv2.imshow('Robot Emotions', frame)
                    if cv2.waitKey(delay) & 0xFF == ord('q'):
                        self.running = False
                        return
            
            # For non-looping emotions, hold last frame briefly then exit
            if not should_loop:
                if frame is not None:
                    cv2.waitKey(500)  # Hold last frame for 500ms
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
        """Initialize and run the robot emotions display"""
        # Set up display window
        cv2.namedWindow('Robot Emotions', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Robot Emotions', self.screen_width, self.target_screen_height)
        
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
        while self.running:
            if not self.command_queue.empty():
                command = self.command_queue.get().strip()
                if command == 'boot':
                    self.play_emotion('bootup')
                    self.play_neutral_loop()
                elif command in ['exit', 'quit']:
                    break

        # Cleanup on exit
        self.running = False
        cv2.destroyAllWindows()
        sys.exit(0)

if __name__ == "__main__":
    robot = RobotEmotions()
    robot.run()