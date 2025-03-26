import RPi.GPIO as GPIO
import time

# LCD Pin Configuration
LCD_RS = 25
LCD_E = 24
LCD_D4 = 23
LCD_D5 = 22
LCD_D6 = 27
LCD_D7 = 18

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

class LCDTest:
    def __init__(self):
        """Initialize GPIO and LCD"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Set up GPIO pins
        GPIO.setup(LCD_RS, GPIO.OUT)
        GPIO.setup(LCD_E, GPIO.OUT)
        GPIO.setup(LCD_D4, GPIO.OUT)
        GPIO.setup(LCD_D5, GPIO.OUT)
        GPIO.setup(LCD_D6, GPIO.OUT)
        GPIO.setup(LCD_D7, GPIO.OUT)

        # Initialize display
        self.lcd_init()

    def lcd_init(self):
        """Initialize LCD"""
        # Initialization sequence
        self.lcd_byte(0x33, LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32, LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06, LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C, LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28, LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, LCD_CMD) # 000001 Clear display
        time.sleep(E_DELAY)

    def lcd_byte(self, bits, mode):
        """Send byte to data pins"""
        # Prepare pins
        GPIO.output(LCD_RS, mode) # RS

        # High bits
        GPIO.output(LCD_D4, False)
        GPIO.output(LCD_D5, False)
        GPIO.output(LCD_D6, False)
        GPIO.output(LCD_D7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(LCD_D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(LCD_D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(LCD_D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        GPIO.output(LCD_D4, False)
        GPIO.output(LCD_D5, False)
        GPIO.output(LCD_D6, False)
        GPIO.output(LCD_D7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(LCD_D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(LCD_D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(LCD_D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
        """Toggle enable"""
        time.sleep(E_DELAY)
        GPIO.output(LCD_E, True)
        time.sleep(E_PULSE)
        GPIO.output(LCD_E, False)
        time.sleep(E_DELAY)

    def lcd_string(self, message, line):
        """Send string to display"""
        message = message.ljust(LCD_WIDTH," ")
        self.lcd_byte(line, LCD_CMD)
        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message[i]), LCD_CHR)

    def test_lcd(self):
        """Test LCD functionalities"""
        try:
            print("Starting LCD Test")
            
            # Clear Display
            self.lcd_byte(0x01, LCD_CMD)
            
            # Display Test Messages
            print("Displaying Test Message 1")
            self.lcd_string("Hello, World!", LCD_LINE_1)
            time.sleep(2)
            
            print("Displaying Test Message 2")
            self.lcd_string("LCD Screen Test", LCD_LINE_1)
            self.lcd_string("Raspberry Pi", LCD_LINE_2)
            time.sleep(2)
            
            # Scrolling Test
            print("Performing Scrolling Test")
            test_msg = "This is a scrolling test message for LCD screen"
            for i in range(len(test_msg) - LCD_WIDTH + 1):
                self.lcd_string(test_msg[i:i+LCD_WIDTH], LCD_LINE_1)
                time.sleep(0.3)
            
            # Final Clear
            self.lcd_byte(0x01, LCD_CMD)
            self.lcd_string("Test Complete!", LCD_LINE_1)
            time.sleep(2)
            
            # Final Clear
            self.lcd_byte(0x01, LCD_CMD)
            
        except KeyboardInterrupt:
            print("LCD Test Interrupted")
        finally:
            GPIO.cleanup()

def main():
    lcd_test = LCDTest()
    lcd_test.test_lcd()

if __name__ == "__main__":
    main()