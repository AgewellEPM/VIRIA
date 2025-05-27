import time

# Optional Raspberry Pi GPIO support
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# Optional serial support for Arduino
try:
    import serial
    SERIAL_AVAILABLE = True
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except:
    SERIAL_AVAILABLE = False
    arduino = None

class AnimatronicController:
    def __init__(self):
        self.led_pins = {
            "joy": 17,
            "rage": 27,
            "calm": 22,
            "sacred": 23
        }
        if GPIO_AVAILABLE:
            for pin in self.led_pins.values():
                GPIO.setup(pin, GPIO.OUT)

    def trigger_emotion(self, emotion):
        print(f"[⚙️] Activating physical output for emotion: {emotion}")

        if GPIO_AVAILABLE:
            self._flash_led(self.led_pins.get(emotion))

        if SERIAL_AVAILABLE and arduino:
            arduino.write(f"{emotion}\n".encode())

    def _flash_led(self, pin, duration=1.0):
        if pin is None:
            return
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)

    def cleanup(self):
        if GPIO_AVAILABLE:
            GPIO.cleanup()

# --- Example usage ---
if __name__ == "__main__":
    controller = AnimatronicController()
    try:
        emotions = ["joy", "rage", "calm", "sacred"]
        for e in emotions:
            controller.trigger_emotion(e)
            time.sleep(2)
    finally:
        controller.cleanup()
