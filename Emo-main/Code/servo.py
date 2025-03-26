import board
import busio
from adafruit_servokit import ServoKit
import time

class ServoTest:
    def __init__(self, channels=16, address=0x40):
        """
        Initialize Servo Driver
        :param channels: Number of channels on the servo driver
        :param address: I2C address of the servo driver
        """
        # Initialize I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize ServoKit
        self.kit = ServoKit(channels=channels, address=address)

    def test_individual_servo(self, channel, servo_type='SG90'):
        """
        Test an individual servo motor
        :param channel: Servo channel to test
        :param servo_type: Type of servo (SG90 or MG90)
        """
        print(f"Testing Servo on Channel {channel} ({servo_type})")
        
        # Servo angle ranges might vary slightly
        if servo_type == 'SG90':
            angles = [0, 45, 90, 135, 180]
        elif servo_type == 'MG90':
            angles = [0, 60, 90, 120, 180]
        else:
            raise ValueError("Unsupported servo type")

        try:
            for angle in angles:
                print(f"Moving to {angle} degrees")
                self.kit.servo[channel].angle = angle
                time.sleep(1)
            
            # Return to neutral position
            self.kit.servo[channel].angle = 90
            time.sleep(1)
        except Exception as e:
            print(f"Error testing servo: {e}")

    def run_full_test(self):
        """Run test on multiple servos"""
        print("Starting Servo Motor Test")
        
        # Test 2 SG90 servos
        self.test_individual_servo(0, 'SG90')
        time.sleep(1)
        self.test_individual_servo(1, 'SG90')
        time.sleep(1)
        
        # Test 1 MG90 servo
        self.test_individual_servo(2, 'MG90')
        
        print("Servo Motor Test Complete")

def main():
    servo_test = ServoTest()
    servo_test.run_full_test()

if __name__ == "__main__":
    main()