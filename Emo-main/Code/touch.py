import RPi.GPIO as GPIO
import time

# Capacitive Touch Sensor Configuration
TOUCH_SENSOR_PIN = 17

def setup_touch_sensor():
    """Setup GPIO for touch sensor"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TOUCH_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def test_touch_sensor():
    """Test touch sensor functionality"""
    try:
        setup_touch_sensor()
        print("Touch Sensor Test Started")
        print("Press Ctrl+C to exit")
        
        touch_count = 0
        while True:
            # Read touch sensor state
            touch_state = GPIO.input(TOUCH_SENSOR_PIN)
            
            if touch_state == GPIO.HIGH:
                touch_count += 1
                print(f"Touch Detected! Count: {touch_count}")
                # Wait to prevent multiple triggers
                time.sleep(0.5)
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nTouch Sensor Test Stopped")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_touch_sensor()